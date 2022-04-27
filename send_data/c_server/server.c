/* server.c */

#include <sys/socket.h>
#include <arpa/inet.h> //inet_addr
#include <unistd.h>    //write

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#pragma pack(1)

#include "rp.h"

typedef struct payload_t {
    float data1;
    float data2;
    float data3;
    float data4;
} payload;

#pragma pack()


int createSocket(int port)
{
    int sock, err;
    struct sockaddr_in server;

    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0)
    {
        printf("ERROR: Socket creation failed\n");
        exit(1);
    }
    printf("Socket created\n");

    bzero((char *) &server, sizeof(server));
    server.sin_family = AF_INET;
    server.sin_addr.s_addr = INADDR_ANY;
    server.sin_port = htons(port);
    if (bind(sock, (struct sockaddr *)&server , sizeof(server)) < 0)
    {
        printf("ERROR: Bind failed\n");
        exit(1);
    }
    printf("Bind done\n");

    listen(sock , 3);

    return sock;
}

void closeSocket(int sock)
{
    close(sock);
    return;
}

void sendMsg(int sock, void* msg, uint32_t msgsize)
{
    if (write(sock, msg, msgsize) < 0)
    {
        printf("Can't send message.\n");
        closeSocket(sock);
        exit(1);
    }
    //printf("Message sent (%d bytes).\n", msgsize);
    return;
}

int main()
{
    int PORT = 2300;
    int BUFFSIZE = 512;
    char buff[BUFFSIZE];
    int ssock, csock;
    int nread;
    struct sockaddr_in client;
    int clilen = sizeof(client);

    // Initialization of API
    if (rp_Init() != RP_OK) {
        fprintf(stderr, "Red Pitaya API init failed!\n");
        return EXIT_FAILURE;
    }

    ssock = createSocket(PORT);
    printf("Server listening on port %d\n", PORT);

    while (1)
    {
        csock = accept(ssock, (struct sockaddr *)&client, &clilen);
        if (csock < 0)
        {
            printf("Error: accept() failed\n");
            continue;
        }

        printf("Accepted connection from %s\n", inet_ntoa(client.sin_addr));
        bzero(buff, BUFFSIZE);
        /*
        while ((nread=read(csock, buff, BUFFSIZE)) > 0)
        {
            printf("\nReceived %d bytes\n", nread);
            payload *p = (payload*) buff;
            printf("Received contents: id=%d, counter=%d, temp=%f\n",
                    p->id, p->counter, p->temp);

            printf("Sending it back.. ");
            sendMsg(csock, p, sizeof(payload));
        } */
        for(int i=0; i<1000; i++)
        {
            payload p;
            p.data1 = i;
            // p.data2 = i+1;
            rp_AIpinGetValue(0, &p.data2);
            p.data3 = i+2;
            p.data4 = i+3;

            sendMsg(csock, &p, sizeof(payload));
        }

        printf("Closing connection to client\n");
        printf("----------------------------\n");
        closeSocket(csock);
        rp_Release();
    }

    closeSocket(ssock);
    printf("bye");
    return 0;
}
