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
    float id;
    float input0;
    float input1;
    float input2;
    float input3;
    float fast1;
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

float acquireFastInput()
{
    uint32_t buff_size = 10;
    float *buff = (float *)malloc(buff_size * sizeof(float));

    rp_AcqReset();
    rp_AcqSetDecimation(RP_DEC_8);
    rp_AcqSetTriggerLevel(0.1); //Trig level is set in Volts while in SCPI
    rp_AcqSetTriggerDelay(0);

    rp_AcqStart();

    sleep(0.001)

    p_AcqGetOldestDataV(RP_CH_1, &buff_size, buff);
    float value = buff[0];
    free(buff);

    return value;
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

        // for(int i=0; i<1000; i++)
        while(1)
        {
            payload p;
            p.id = i;
            //rp_AIpinGetValue(0, &p.input0);
            //rp_AIpinGetValue(1, &p.input1);
            //rp_AIpinGetValue(2, &p.input2);
            //rp_AIpinGetValue(3, &p.input3);
            p.fast1 = acquireFastInput();

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
