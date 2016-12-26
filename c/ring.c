#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <memory.h>
#include <time.h>
#include <limits.h>
#include <pthread.h>
#include <mpi.h>
#include <unistd.h>

#define DEBUG_STATEMENT(X)
//#define DEBUG_STATEMENT(X) X

#define BUFFER_SIZE 12

pthread_mutex_t lock;

enum message_type
{
    REQUEST,
    RESPONSE,
    LEADER_ELECTION_DONE,
    TYPE_MAX,
};

const char* TYPE_NAME[TYPE_MAX] =
{
    "REQUEST",
    "RESPONSE",
    "LEADER_ELECTION_DONE",
};

struct mpi_message
{
    int type;
    int sender;
    int sender_priority;
};

int pack_mpi_message(const struct mpi_message* msg, void* buffer, int bufsize)
{
    int pos = 0;
    memset(buffer, 0, bufsize);

    MPI_Pack(&msg->type, 1, MPI_INT, buffer, bufsize, &pos, MPI_COMM_WORLD);
    MPI_Pack(&msg->sender, 1, MPI_INT, buffer, bufsize, &pos, MPI_COMM_WORLD);
    MPI_Pack(&msg->sender_priority, 1, MPI_INT, buffer, bufsize, &pos, MPI_COMM_WORLD);

    return pos;
}

void unpack_mpi_message(struct mpi_message* msg, const void* buffer, int bufsize)
{
    int pos = 0;
    memset(msg, 0, sizeof(struct mpi_message));

    MPI_Unpack(buffer, bufsize, &pos, &msg->type, 1, MPI_INT, MPI_COMM_WORLD);
    MPI_Unpack(buffer, bufsize, &pos, &msg->sender, 1, MPI_INT, MPI_COMM_WORLD);
    MPI_Unpack(buffer, bufsize, &pos, &msg->sender_priority, 1, MPI_INT, MPI_COMM_WORLD);
}

struct thread_arg
{
    int rank;
    int size;
    int my_priority;
};

void* node(void* arg)
{
    struct thread_arg *arg_ = (struct thread_arg*)arg; 
    int rank, size, my_priority;
    if (arg_)
    {
        rank = arg_->rank;
        size = arg_->size;
        my_priority = arg_->my_priority;
    } 
    else
    {
        printf("arg is NULL");
        return 0;
    }
    int recv_priority = -1;

    struct mpi_message message;
    memset(&message, 0, sizeof(message));

    char buffer[BUFFER_SIZE];

    int loop_count = 0;
    int dest = (rank + 1) % size;

    if(rank == dest)
    {
        printf("I'm [0], I AM THE LEADER!\n");
        return 0;
    }
    else
    {    
        message.sender = rank;
        message.type = REQUEST;
        message.sender_priority = my_priority;
        int pos = pack_mpi_message(&message, buffer, sizeof(buffer));
        MPI_Send(buffer, pos, MPI_PACKED, dest, 0, MPI_COMM_WORLD);

        while(loop_count < size*2)
        {
            MPI_Recv(buffer, sizeof(buffer), MPI_PACKED, MPI_ANY_SOURCE, MPI_ANY_TAG, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
            unpack_mpi_message(&message, buffer, sizeof(buffer));
            printf("I'm %d, received TYPE[%s], SENDER[%d]\n", rank, TYPE_NAME[message.type], message.sender);

            if(message.type == REQUEST)
            {
                recv_priority = message.sender_priority;
                int sender = message.sender;
                message.sender = rank;
                message.sender_priority = my_priority;


                if(recv_priority > my_priority)
                {
                    message.sender = rank;
                    message.type = REQUEST;
                    message.sender_priority = recv_priority;
                    pos = pack_mpi_message(&message, buffer, sizeof(buffer));

                    MPI_Send(buffer, pos, MPI_PACKED, dest, 0, MPI_COMM_WORLD); 
                }
                else if (recv_priority == my_priority)
                {
                    printf("I AM [%d], I AM THE LEADER!\n", rank);
                    message.sender = rank;
                    message.type = LEADER_ELECTION_DONE;
                    message.sender_priority = rank;
                    pos = pack_mpi_message(&message, buffer, sizeof(buffer));

                    MPI_Send(buffer, pos, MPI_PACKED, dest, 0, MPI_COMM_WORLD);
                    break;
                }
            }

            else if (message.type == LEADER_ELECTION_DONE)
            {
                printf("I AM [%d], OUR LEADER IS [%d], ELECTION IS DONE!\n", rank, message.sender_priority);
                message.sender = rank;
                message.type = LEADER_ELECTION_DONE;
                pos = pack_mpi_message(&message, buffer, sizeof(buffer));

                MPI_Send(buffer, pos, MPI_PACKED, dest, 0, MPI_COMM_WORLD);
                break;
            }
            loop_count++;
        }
    }
    return 0;
}


int main(int argc, char** argv)
{
    int rank, size;

    MPI_Init (&argc, &argv);
    MPI_Comm_rank (MPI_COMM_WORLD, &rank);
    MPI_Comm_size (MPI_COMM_WORLD, &size);

    srandom(time(0) + rank);
    int my_priority = random();

    printf("Hello world from process %d of %d, priority %d\n", rank, size, my_priority);

    pthread_t thread;

    struct thread_arg *arg = malloc(sizeof(struct thread_arg));
    arg->my_priority = my_priority;
    arg->rank = rank;
    arg->size = size;
    pthread_create(&thread, 0, node, arg);
    void* ret;
    pthread_join(thread, &ret);
    fflush(0);
    MPI_Finalize();
    return 0;
}

