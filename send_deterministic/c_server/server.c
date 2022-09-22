
/* server.c */

#include <sys/socket.h>
#include <arpa/inet.h> //inet_addr
#include <unistd.h>    //write

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#pragma pack(1)

#include "rp.h"

typedef struct payload_t {
    float id;
    float input0[200];
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
        // printf("Can't send message.\n");
        // closeSocket(sock);
        // exit(1);
	return;
    }

    //printf("Message sent (%d bytes).\n", msgsize);
    return;
}

float acquireFastInput(int channel) // acquires data from fast input
{
    uint32_t buff_size = 1; // buffer for writing fast input data
    float *buff = (float *)malloc(buff_size * sizeof(float)); // allocate buffer space, see RP docs example

    rp_AcqReset();
    rp_AcqSetDecimation(RP_DEC_8);
    rp_AcqSetTriggerLevel(channel, 0); //Trig level is set in Volts while in SCPI
    rp_AcqSetTriggerDelay(0);

    rp_AcqStart();
    sleep(0.00001); // determine correct sleep time that the buffer can be read

    rp_AcqGetOldestDataV(RP_CH_1, &buff_size, buff);
    float value = buff[0];
    free(buff);

    //printf("Value = %f\n", value);
    return value;
}

void startGenerator() // start sine generator on output
{
    rp_GenReset();
    rp_GenFreq(RP_CH_1, 0.5);
    rp_GenAmp(RP_CH_1, 1.0);
    rp_GenWaveform(RP_CH_1, RP_WAVEFORM_SINE);
    rp_GenOutEnable(RP_CH_1);
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

    clock_t start_t, end_t;
    double total_t;

    float fast2;
    clock_t start, end;
    double cpu_time_used;

    // Initialization of API
    if (rp_Init() != RP_OK) {
        fprintf(stderr, "Red Pitaya API init failed!\n");
        return EXIT_FAILURE;
    }

    ssock = createSocket(PORT);
    printf("Server listening on port %d\n", PORT);

    // startGenerator(); // start sine generator on output

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
	int sent = 0;
        // for(int i=0; i<1000; i++)
        while(1) // infinite loop possible when client closes the connection after a specific event
            // e.g. a pre-determined number of samples was read or an input was performed
        {
	    //sleep(0.00001);
	    start_t = clock();
            payload p;
            //p.id = i;
	    //start = clock();
	    for( int i = 0; i < 200; i++)
	    {
		start_t = clock();
	        rp_AIpinGetValue(0, &p.input0[i]);
		while(clock() < start_t + 496){}
	    }
            //rp_AIpinGetValue(0, &p.input0);
            //rp_AIpinGetValue(1, &p.input1);
            //rp_AIpinGetValue(2, &p.input2);
            //rp_AIpinGetValue(3, &p.input3);
	    // printf("Cpu time used: %f \n", cpu_time_used);
	    // printf("Value of input0: %1.2fV\n", p.input0);
            //p.fast1 = acquireFastInput(1);
	    //fast2 = acquireFastInput(2);
	    //printf("clocks per sec: %d \n", CLOCKS_PER_SEC);
	    //cpu_time_used = ((double) (end-start)) / CLOCKS_PER_SEC;
	    //start_t = clock();
            sendMsg(csock, &p, sizeof(payload));
	    //while(clock() < start_t + 999){}
	    //end_t = clock();
	    //total_t = (double)(end_t - start_t) / CLOCKS_PER_SEC;
	    //printf("Time taken by CPU: %f\n", total_t);
        }

        printf("Closing connection to client\n");
        printf("----------------------------\n");
        closeSocket(csock);
        rp_Release();
    }
    rp_Release();

    closeSocket(ssock);
    printf("bye");
    return 0;
}
