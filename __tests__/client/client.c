#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>
#include <string.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <signal.h>
#include <errno.h>
#include <netinet/tcp.h>
#include <time.h>
#include <getopt.h>
#include <stdbool.h>
#include <pthread.h>
#include <string.h>

#include "../tools/connection.h"
#include "../tools/log.h"

static pthread_t t_id;
static int client_fd;

/* ********************************************************* */
void stop_child_thread()
{
    int ret = pthread_join(t_id, NULL); /* Stop the message receveing handler thread */
    if (!ret)
    {
        LOG(_LOG_INFO_, "Receive message handler thread stopped");
    }
    else
    {
        LOG(_LOG_ERR_, "Could not stop receive message handler thread");
    }
}
/* ******************************************* */

/* stop the service on SIGINT command */
void sigint_handler(int sig)
{
    send(client_fd, "/quit", 5, 0); /* Server needs to stop its service for the client too */
    stop_child_thread();            /* Stop the message receveing handler thread */

    close(client_fd);
    exit(EXIT_SUCCESS);
}

/* ****************************************************** */

/* Thread to handle receive messages from other clients asynchronously */
void *rcv_msg_handler(void *arguments)
{
    char name[MAX_USERNAME_LEN], rcvd_msg[MAX_MSG_LEN];
    int rcvd_bytes;

    memset(name, '\0', MAX_USERNAME_LEN);

    struct args *p_args = (struct args *)arguments;
    strncpy(name, p_args->name, strlen(p_args->name) + 1);

    while (1)
    {
        memset(rcvd_msg, '\0', MAX_MSG_LEN);

        rcvd_bytes = recv(client_fd, &rcvd_msg, sizeof(rcvd_msg), 0);
        if (rcvd_bytes > 0)
        {
            strip_newline(rcvd_msg);
            if (strlen(rcvd_msg))
            {
                printf("\n\x1b[35m%s@server:~$\x1b[0m%s", name, rcvd_msg);
                fflush(stdout);
            }
        }
    }
}

/* ***************************************************************************************** */

int main(int argc, char *argv[])
{
    char server_ip[INET_ADDRSTRLEN], server_port[5], name[MAX_USERNAME_LEN], greetings_from_server[100], buff[MAX_MSG_LEN];

    int opt, port, debug_level, connect_status, sent_bytes, recv_bytes, temp_return_value, n;

    bool server_ip_flag = false, server_port_flag = false,
         debug_level_flag = false, name_flag = false;

    char *strptr;

    struct sockaddr_in server_addr;
    struct args thread_args;

    memset(&server_addr, 0, sizeof(server_addr));
    memset(server_ip, '\0', sizeof(server_ip));
    memset(server_port, '\0', sizeof(server_port));
    memset(name, '\0', sizeof(name));
    memset(buff, '\0', sizeof(buff));

    while ((opt = getopt(argc, argv, "-a:p:D:n:")) != -1)
    {
        switch (opt)
        {
        case 'p':
            server_port_flag = true;
            strncpy(server_port, optarg, 4);
            LOG(_LOG_INFO_, "provided port number: %s", server_port);
            break;
        case 'a':
            server_ip_flag = true;
            strncpy(server_ip, optarg, INET_ADDRSTRLEN);
            LOG(_LOG_INFO_, "provided IP: %s", server_ip);
            break;

        case 'n':
            name_flag = true;
            strncpy(name, optarg, strlen(optarg) + 1);
            LOG(_LOG_INFO_, "provided name for the client: %s", name);
            break;

        case 'D':
            debug_level_flag = true;
            char *buff1;
            char temp[5];
            memset(temp, '\0', sizeof(temp));
            strncpy(temp, optarg, 4);
            debug_level = strtol(temp, &buff1, 10);
            LOG(_LOG_INFO_, "provided debug level value: %d", debug_level);

            if (debug_level < 0)
                debug_level = 1;
            if (debug_level > 3)
                debug_level = 3;

            SET_LOG_LEVEL(debug_level);
            buff1 = NULL;
            break;
        case '?':
            break;
        case ':':
            LOG(_LOG_WARN_, "Missing arg for %c", optopt);
            exit(EXIT_FAILURE);
        case 1:
            LOG(_LOG_ERR_, " USAGE: <server address> <port> <name> <debug level>");
            break;
        }
    }

    /*  If any arguments missing, print usage guide and quit */
    if (!server_ip_flag || !server_port_flag || !debug_level_flag || !name_flag)
    {
        LOG(_LOG_ERR_, " USAGE: <server address> <port> <name> <debug level>");
        exit(EXIT_FAILURE);
    }

    /* Convert "localhost" to "0.0.0.0" */
    if (strncmp(server_ip, "localhost", 9) == 0)
    {
        bzero(server_ip, sizeof(server_ip));
        strcpy(server_ip, "0.0.0.0");
        LOG(_LOG_INFO_, "connection request to a local server");
    }

    port = strtol(server_port, &strptr, 10);

    server_addr.sin_family = AF_INET;

    /*  assign the same port where the server is running */
    server_addr.sin_port = htons(port);

    /* IP presentation format to network format */
    temp_return_value = inet_pton(AF_INET, server_ip, &server_addr.sin_addr);

    if (temp_return_value <= 0)
    {
        if (temp_return_value == 0)
            LOG(_LOG_ERR_, "server IP is Not in presentation format");
        exit(EXIT_FAILURE);
    }

    client_fd = socket(AF_INET, SOCK_STREAM, 0);

    /* Send a total of 2 SYN packets => Timeout ~7s */
    int synRetries = 2;
    setsockopt(client_fd, IPPROTO_TCP, TCP_SYNCNT, &synRetries, sizeof(synRetries));

    if (client_fd < 0)
    {
        LOG(_LOG_ERR_, "Error in creating socket");
        exit(EXIT_FAILURE);
    }

    LOG(_LOG_INFO_, "Connection request sent, waiting for server to respond");
    connect_status = connect(client_fd, (struct sockaddr *)&server_addr, sizeof(server_addr));

    if (connect_status < 0)
    {
        LOG(_LOG_ERR_, "could not connect to the server");
        exit(EXIT_FAILURE);
    }

    /* send client's name to the server */
    sent_bytes = send(client_fd, &name, strlen(name), 0);
    if (sent_bytes == -1)
    {
        LOG(_LOG_ERR_, "could not sent the name");
        close(client_fd);
        exit(EXIT_FAILURE);
    }

    /* Waiting for the server to greet with the name it recently sent */
    recv_bytes = recv(client_fd, &greetings_from_server, sizeof(greetings_from_server), 0);
    if (recv_bytes < 0)
    {
        LOG(_LOG_ERR_, "could not established the connection properly");
        close(client_fd);
        exit(EXIT_FAILURE);
    }
    else
    {
        LOG(_LOG_INFO_, "%s", greetings_from_server);
    }

    /* Protocol defined handshaking is done, 
    provide a virtual terminal for the actual conversation */
    LOG(_LOG_INFO_, "Remote Terminal is Ready");
    LOG(_LOG_INFO_, "Type your message (Type '!q' or hit ^C to quit):");

    /* Prepare the arguments for the rcv_msg_handler thread */
    thread_args.client_fd = client_fd;
    strncpy(thread_args.name, name, strlen(name));

    if (pthread_create(&t_id, NULL, rcv_msg_handler, (void *)&thread_args) != 0)
    {
        LOG(_LOG_ERR_, "couldn't create the Thread %ld\n", t_id);
        exit(EXIT_FAILURE);
    }

    LOG(_LOG_INFO_, "New thread created to receive messages");

    while (1)
    {
        n = 0;
        bzero(buff, MAX_MSG_LEN);
        signal(SIGINT, sigint_handler);
        printf("\x1b[35m%s@SERVER:~$\x1b[0m", name); /* virtual terminal */
        fflush(stdout);

        while ((buff[n++] = getchar()) != '\n')
            ;

        strip_newline(buff);
        if (!strlen(buff) || !strncmp(buff, " ", 1) || !strncmp(buff, "\n", 1))
        {
            /* it's a blank message, don't send it */
            continue;
        }

        /* only if it is a /help command, skip sending it to the server */
        if (!strncmp(buff, "/help", 5))
        {
            printf("\x1b[35m%s@SERVER:~$%s\x1b[0m", name, "1./connect <username>: to connect to a user 2./quit: to exit 3./help: to show this help message\n");
            continue;
        }
        sent_bytes = send(client_fd, &buff, sizeof(buff), 0); /* Send the message to the server */
        if (sent_bytes == -1)
        {
            LOG(_LOG_WARN_, "could not sent the last message try again");
        }

        /* even /quit command needs to be sent to server to inform server
        that the client is about to quit */

        /* Now check if the last message was a quit command
        if it was, quit the client and */
        if (strncmp(buff, "/quit", 5) == 0)
        {
            // FIXME stop child too
            close(client_fd);
            LOG(_LOG_INFO_, "Terminated");
            exit(EXIT_SUCCESS);
            /* Close the child thread too */
            stop_child_thread();
        }
    }

    return 0;
}