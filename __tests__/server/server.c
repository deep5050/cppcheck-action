#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <string.h>
#include <netdb.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <signal.h>
#include <errno.h>
#include <sys/wait.h>
#include <sys/time.h>
#include <time.h>
#include <pthread.h>
#include <getopt.h>
#include <stdbool.h>

#include "../tools/log.h"
#include "../tools/connection.h"

#define MAX_THREAD_COUNT 20

static int thread_count = -1;
static pthread_t threads_pool[MAX_THREAD_COUNT];

void kill_all_threads()
{
    int killed_threads = 0;
    for (int i = 0; i <= thread_count; i++)
    {
        int return_val = pthread_cancel(threads_pool[i]);
        if (return_val != ESRCH)
            killed_threads++;
    }
    if (killed_threads)
        LOG(_LOG_WARN_, "%d threads did not shutdown properly", killed_threads);
    else
        LOG(_LOG_INFO_, "All threads exited successfully");
}

void INTR_handler(int sig)
{
    //TODO clear the database
    kill_all_threads();
    close(server_fd);
    LOG(_LOG_INFO_, "SERVER CLOSED");
    exit(0);
}

/* *************************************************** */

int main(int argc, char *argv[])
{

    int opt, backlog, debug_level;
    bool port_flag = false, backlog_flag = false, debug_level_flag = false;

    char port[5];
    memset(port, '\0', sizeof(port));

    while ((opt = getopt(argc, argv, "-p:b:D:")) != -1)
    {
        switch (opt)
        {
        case 'p':
            port_flag = true;
            strncpy(port, optarg, 4);
            LOG(_LOG_INFO_, "provided port number: %s", port);
            break;
        case 'b':
            backlog_flag = true;
            char *buff;
            char temp[5];
            memset(temp, '\0', sizeof(temp));
            strncpy(temp, optarg, 4);
            backlog = strtol(temp, &buff, 10);
            LOG(_LOG_INFO_, "provided backlog value: %d", backlog);
            buff = NULL;
            break;
        case 'D':
            debug_level_flag = true;
            char *buff1;
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
            LOG(_LOG_ERR_, " USAGE: <portno> <backlog> <debug level>");
            break;
        }
    }

    if (!backlog_flag || !port_flag || !debug_level_flag)
    {
        LOG(_LOG_ERR_, "port, backlog and debug level values are mandatory");
        exit(EXIT_FAILURE);
    }

    /* Initializing all the variables only it passes the getopt() checking */
    int client_fd, server_status, bind_status, listen_status, accept_status,
        addr_status, n = 0, yes = 1, bytes_sent;

    /* Initializing all the queues */
    STAILQ_INIT(&head);
    STAILQ_INIT(&message_head);

    pthread_t t_id; /* Child thread ID */
    struct addrinfo server_addr, *results, *p;
    struct sockaddr_in client_addr;
    struct args thread_args; /* Child treads argument holder */
    memset(&thread_args, 0, sizeof(thread_args));

    socklen_t client_addr_size = sizeof(client_addr);

    char buff[MAX_MSG_LEN], addr[INET_ADDRSTRLEN];

    memset(&server_addr, 0, sizeof(server_addr));
    memset(&client_addr, 0, sizeof(client_addr));

    server_addr.ai_family = PF_INET;       /* IPv4 */
    server_addr.ai_socktype = SOCK_STREAM; /* tcp Stream */
    server_addr.ai_flags = AI_PASSIVE;     /* fill ip automatically */

    /* get all the available address of this machine */

    if ((addr_status = getaddrinfo(NULL, port, &server_addr, &results)) != 0)
    {
        LOG(_LOG_ERR_, "getaddrinfo(): %s", gai_strerror(addr_status));
        exit(EXIT_FAILURE);
    }

    /* bind a socket at the first available address */
    for (p = results; p != NULL; p = p->ai_next)
    {

        inet_ntop(p->ai_family, p->ai_addr, addr, sizeof(addr));
        LOG(_LOG_INFO_, "Trying to build on %s", addr);

        if ((server_fd = socket(p->ai_family, p->ai_socktype, p->ai_protocol)) == -1)
        {
            continue; /* if socket can not be created on this address try another */
        }
        if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(int)) == -1)
        {
            LOG(_LOG_ERR_, "Error ocurred under setsockopt()");
            exit(EXIT_FAILURE);
        }

        if (((bind_status = bind(server_fd, p->ai_addr, p->ai_addrlen)) == -1))
        {
            // LOG(_LOG_ERR_,"error ocurred under bind()");
            continue;
        }

        /**
         * control reaches here if all the above conditions satifie
         * we have successfully bound a socket and can exit from this loop
         */
        inet_ntop(p->ai_family, p->ai_addr, addr, sizeof(addr));
        break;
    }

    freeaddrinfo(results);

    /**
     * if we get p== NULL that means we couldn't bind to any of the addresses
     * should return from the program
     */

    if (p == NULL)
    {
        LOG(_LOG_ERR_, "Couldn't build a server");
        exit(EXIT_FAILURE);
    }

    listen_status = listen(server_fd, backlog);
    if (listen_status == -1)
    {
        LOG(_LOG_ERR_, "Error ocurred under listen()");
        exit(EXIT_FAILURE);
    }

    /* If control reaches here, everything is Ok */
    LOG(_LOG_INFO_, "UP and LISTENING on %s:%s with BACKLOG %d", addr, port, backlog);

    char greetings[] = "SERVER: Hi client,you are now connected";
    char sorry[] = "SERVER: sorry could not give the service right now";

    LOG(_LOG_INFO_, "SERVER is Waiting for connections");

    while (1)
    {
        signal(SIGINT, INTR_handler);

        inet_ntop(client_addr.sin_family, &client_addr.sin_addr.s_addr, addr, sizeof(addr));

        client_fd = accept(server_fd, (struct sockaddr *)&client_addr, &client_addr_size);
        if (client_fd < 0)
        {
            // perror("ERROR:");
            LOG(_LOG_ERR_, "Could not connect to the client properly, fd: %d", client_fd);
            continue;
        }

        LOG(_LOG_INFO_, "NEW CLIENT: ID(%d): %s:%d", client_fd, addr, ntohs(client_addr.sin_port));

        /* Filling the thread argument */
        thread_args.client_fd = client_fd;
        thread_args.name[0] = '\0'; /* As we don't know the username of the client yet, 
        will be filled up later by the child thread */

        /* A thread is created to handle full duplex communication with a new client */
        if (pthread_create(&t_id, NULL, service_clients, (void *)&thread_args) != 0)
        {
            LOG(_LOG_ERR_, "couldn't create the Thread %ld\n", t_id);
            send(client_fd, sorry, sizeof(sorry), 0);
            close(client_fd);
            continue;
        }

        LOG(_LOG_INFO_, "New thread created: %ld to service client ID %d", t_id, client_fd);
        pthread_detach(t_id);
        threads_pool[++thread_count] = t_id;
    }

    return 0;
}
