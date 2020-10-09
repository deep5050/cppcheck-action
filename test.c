#include <arpa/inet.h>
#include <errno.h>
#include <netdb.h>
#include <netinet/in.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>
#define max_mssg_len 1024

int server_fd;

char *timestamp() {
  struct tm *local;
  time_t t = time(NULL);
  char *str;

  /* Get the localtime */
  local = localtime(&t);
  str = asctime(local);

  int i = 0;
  int len = strlen(str) + 1;

  for (i = 0; i < len; i++) {
    if (str[i] == '\n') {
      /* Move all the char following the char "\n" by one to the left. */
      strncpy(&str[i], &str[i + 1], len - i);
    }
  }

  return str;
}

void sigchld_handler(int s) {
  /* waitpid() might overwrite errno, so we save and restore it: */
  int saved_errno = errno;

  while (waitpid(-1, NULL, WNOHANG) > 0)
    ;
  errno = saved_errno;
}

#ifdef THREAD
#include <pthread.h>
#define MAX_THREAD_COUNT 20
struct args {
  int client_fd;
};
int thread_count = -1;
pthread_t threads_pool[MAX_THREAD_COUNT];

void kill_all_threads() {
  int killed_threads = 0;
  for (int i = 0; i <= thread_count; i++) {
    int return_val = pthread_cancel(threads_pool[i]);
    if (return_val != ESRCH)
      killed_threads++;
  }
  if (killed_threads)
    printf("\n[%s] SERVER: %d threads did not shutdown properly\n", timestamp(),
           killed_threads);
  else
    printf("\n[%s] All threads exited successfully\n", timestamp());
}
void *service_clients(void *arguments) {

  struct args *p_args = (struct args *)arguments;

  /**
   * copy the client_fd locally as creation process ( genrerates new fd) of
   * a new thread will chage the value pointed by *argument
   */

  int client_fd;

  client_fd = p_args->client_fd;

  printf("[%s] SERVER: Inside Thread %ld\n", timestamp(), pthread_self());

  int bytes_sent;
  char buff[max_mssg_len];

  char greetings[] = "SERVER: Hi client, you are now connected\n";
  bytes_sent = send(client_fd, &greetings, sizeof(greetings), 0);
  if (bytes_sent == 0) {
    printf("[%s] SERVER: Connection lost with client(%d)\n", timestamp(),
           client_fd - 3);
    exit(EXIT_FAILURE);
  } else if (bytes_sent == -1) {
    perror("SERVER: send()");
    exit(EXIT_FAILURE);
  }

  bzero(buff, max_mssg_len);

  while (1) {
    int bytes_rcvd;
    bytes_rcvd = recv(client_fd, &buff, sizeof(buff), 0);
    if (bytes_rcvd == 0) {
      printf("[%s] SERVER: Connection lost with client(%d)\n", timestamp(),
             client_fd - 3);
      break;
    } else if (bytes_rcvd == -1) {
      perror("SERVER: recv()");
      break;
    }

    if (strncmp(buff, "!q", 2) == 0) {
      close(client_fd);
      printf("[%s] DISCONNECTED: CLIENT(%d)\n", timestamp(), client_fd - 3);
      printf("[%s] SERVER: Exiting from Thread %ld\n", timestamp(),
             pthread_self());
      break;
    }

    fflush(stdout);
    printf("[%s] CLIENT_%d@host:~$%s", timestamp(), client_fd - 3, buff);
    bzero(buff, max_mssg_len);
  }

  /* Pthread_cancel() will clean up all the necessary things for us */
  pthread_cancel(pthread_self());
}

#endif

void INTR_handler(int sig) {
  close(server_fd);
  printf("\n[%s] SERVER CLOSED\n", timestamp());
  exit(0);
}

int main(int argc, char *argv[]) {
  int backlog;

  if (argc != 3) {
    puts("USAGE: <portno> <backlog>");
    exit(EXIT_FAILURE);
  }

  if (argv[1] == "" || argv[1] == NULL) {
    puts("ERROR: Enter a valid port number");
    exit(EXIT_FAILURE);
  }

  if (argv[2] == "" || argv[2] == NULL) {
    puts("ERROR: Enter a valid backlog value");
    exit(EXIT_FAILURE);
  }
  char *strptr;
  backlog = strtol(argv[2], &strptr, 10);

  struct addrinfo server_addr, *results, *p;
  struct sockaddr_in client_addr;
  socklen_t client_addr_size;

  int client_fd, server_status, bind_status, listen_status, accept_status,
      addr_status;
  char buff[max_mssg_len];
  int n = 0, yes = 1;

  int bytes_sent;
  char addr[INET_ADDRSTRLEN];

  memset(&server_addr, 0, sizeof(server_addr));
  memset(&client_addr, 0, sizeof(client_addr));

  /*
          struct addrinfo {
              int              ai_flags;
              int              ai_family;
              int              ai_socktype;
              int              ai_protocol;
              socklen_t        ai_addrlen;
              struct sockaddr *ai_addr;
              char            *ai_canonname;
              struct addrinfo *ai_next;
          };
  */

  server_addr.ai_family = PF_INET;       /* IPv4 */
  server_addr.ai_socktype = SOCK_STREAM; /* tcp Stream */
  server_addr.ai_flags = AI_PASSIVE;     /* fill ip automatically */

  /* get all the available address of this machine */

  if ((addr_status = getaddrinfo(NULL, argv[1], &server_addr, &results)) != 0) {
    printf("[%s] SERVER: ERROR getaddrinfo(): %s\n", timestamp(),
           gai_strerror(addr_status));
    exit(EXIT_FAILURE);
  }

  /* bind a socket at the first available address */
  for (p = results; p != NULL; p = p->ai_next) {

    inet_ntop(p->ai_family, p->ai_addr, addr, sizeof(addr));
    printf("[%s] SERVER: Trying to build on: %s", timestamp(), addr);

    if ((server_fd = socket(p->ai_family, p->ai_socktype, p->ai_protocol)) ==
        -1) {
      perror("ERROR socket()");
      continue; /* if socket can not be created on this address try another */
    }

    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(int)) ==
        -1) {
      perror("ERROR setsockopt()");
      exit(EXIT_FAILURE);
    }

    if (((bind_status = bind(server_fd, p->ai_addr, p->ai_addrlen)) == -1)) {
      perror("ERROR bind()");
      continue;
    }

    /**
     * control reaches here if all the above conditions satifie
     * we have succesfully bound a socket and can exit from this loop
     */

    break;
  }

  freeaddrinfo(results);

  /**
   * if we get p== NULL that means we couldn't bind to any of the addresses
   * should return from the program
   */

  if (p == NULL) {
    puts("\nERROR: Couldn't build a server");
    exit(EXIT_FAILURE);
  }

  if (listen_status = listen(server_fd, backlog) == -1) {
    perror("ERROR listen()");
    exit(EXIT_FAILURE);
  }
  /* handle sigaction */

  printf("\n[%s] SERVER: UP and LISTENING on %s:%s with BACKLOG %d\n",
         timestamp(), addr, argv[1], backlog);

  struct sigaction sa;
  sa.sa_handler = sigchld_handler; /* reap all dead processes */
  sigemptyset(&sa.sa_mask);
  sa.sa_flags = SA_RESTART;

  if (sigaction(SIGCHLD, &sa, NULL) == -1) {
    perror("sigaction");
    exit(1);
  }

  char greetings[] = "SERVER: Hi client, you are now connected\n";

#ifdef THREAD

  struct args thread_args;
  memset(&thread_args, 0, sizeof(thread_args));
#endif

  while (1) {
    signal(SIGINT, INTR_handler);

    inet_ntop(client_addr.sin_family, &client_addr.sin_addr.s_addr, addr,
              sizeof(addr));

    client_fd =
        accept(server_fd, (struct sockaddr *)&client_addr, &client_addr_size);

    printf("[%s] SERVER: NEW CLIENT ID(%d): %s:%d\n", timestamp(),
           client_fd - 3, addr, ntohs(client_addr.sin_port));
    char sorry[] = "SERVER: sorry could not give the service right now\n";

#ifdef PROCESS
    if (fork() == 0) {
      bytes_sent = send(client_fd, &greetings, sizeof(greetings), 0);
      if (bytes_sent == 0) {
        printf("[%s] SERVER: Connection lost with client(%d)\n", timestamp(),
               client_fd - 3);
        exit(EXIT_FAILURE);
      } else if (bytes_sent == -1) {
        perror("SERVER: send()");
        exit(EXIT_FAILURE);
      }

      close(server_fd);
      bzero(buff, max_mssg_len);

      while (1) {
        int bytes_rcvd;

        bytes_rcvd = recv(client_fd, &buff, sizeof(buff), 0);
        if (bytes_rcvd == 0) {
          printf("[%s] SERVER: Connection lost with client(%d)\n", timestamp(),
                 client_fd - 3);
          exit(EXIT_FAILURE);
        } else if (bytes_rcvd == -1) {
          perror("SERVER: recv()");
          exit(EXIT_SUCCESS); // dont think its a failure
        }
        if (strncmp(buff, "!q", 2) == 0) {
          close(client_fd);
          printf("[%s] SERVER: DISCONNECTED: CLIENT(%d)\n", timestamp(),
                 client_fd - 3);
          exit(EXIT_SUCCESS);
        }

        fflush(stdout);
        printf("[%s] CLIENT_%d@host:~$%s", timestamp(), client_fd - 3, buff);
      }
    }

#endif

#ifdef THREAD

    pthread_t t_id;

    thread_args.client_fd = client_fd;

    if (pthread_create(&t_id, NULL, service_clients, (void *)&thread_args) !=
        0) {
      printf("[%s] SERVER: ERROR in creating the Thread %ld\n", timestamp(),
             t_id);
      send(client_fd, sorry, sizeof(sorry), 0);
      close(client_fd);
      continue;
    }

    printf("[%s] SERVER: New thread created: %ld to service client %d\n",
           timestamp(), t_id, client_fd - 3);
    pthread_detach(t_id);
    threads_pool[++thread_count] = t_id;
#endif
  }
  return 0;
}
