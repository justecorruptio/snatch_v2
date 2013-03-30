#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>

char FREQS[] = "ETAONRISHDLFCMUGYPWBVKJXQZ";

typedef struct Node {
    int len;
    void ** children;
} Node;

Node * root;

Node * new_node(){
    return (Node *) calloc(1, sizeof(Node));
}

void * insert_child(Node * node, int nth_child, void * x){
    int i;
    if(nth_child >= node->len){
        if(node->len == 0)
            node->children = (void **)calloc(nth_child + 1, sizeof(void *));
        else {
            node->children = (void **)realloc(node->children, (nth_child + 1) * sizeof(void *));
            for(i = node->len; i < nth_child; i++)
                node->children[i] = 0;
        }
        node->len = nth_child + 1;
    }
    node->children[nth_child] = x;
    return x;
}

int create_hist(char * buf, char * hist){
    int i;

    bzero(hist, 26);

    for(;*buf; buf ++)
        hist[*buf - 'A'] ++;
}

Node * create_tree(FILE * in_file){
    int z, i, n;
    char buf[32];
    char hist[26];

    Node * root;
    Node * cur;

    root = new_node();

    while(fscanf(in_file, "%s\n", buf) != -1){
        create_hist(buf, hist);
        cur = root;
        for(i = 0; i < 26; i ++){
            n = hist[i];
            if(n < cur->len && cur->children[n])
                cur = cur->children[n];
            else
                cur = insert_child(cur, n, new_node());
        }
        insert_child(cur, cur->len, strdup(buf));

        z ++;
        //if(z > 20000) break;
    }
    return root;
}

int is_word(Node * ptr, char * word){
    int i, n;
    char hist[26];

    create_hist(word, hist);

    for(i = 0; i < 26; i++){
        n = hist[i];
        if(n < ptr->len && ptr->children[n])
            ptr = ptr->children[n];
        else
            return 0;
    }

    for(i = 0; i < ptr->len; i++)
        if(!strcmp(word, ptr->children[i]))
            return 1;

    return 0;
}

int _find_steals(Node * ptr, char * hist, char* limit, char level, FILE * out_file){
    int i;

    if(level == 26){
        for(i = 0; i < ptr->len; i++){
            fputs_unlocked((char *)ptr->children[i], out_file);
            fputc_unlocked('\n', out_file);
        }
        return 0;
    }

    for (i = hist[level]; i < ptr->len && !(limit && i > hist[level] + limit[level]); i++)
        if(ptr->children[i])
            _find_steals(ptr->children[i], hist, limit, level + 1, out_file);

    return 0;
}

int find_steals(Node * root, char * word, char * pool, FILE * out_file){
    char hist[26];
    char limit[26];

    create_hist(word, hist);
    if (pool){
        create_hist(pool, limit);
        _find_steals(root, hist, limit, 0, out_file);
    }
    else
        _find_steals(root, hist, 0, 0, out_file);
    return 0;
}

void so_initialize(char * word_file){
    root = create_tree(fopen(word_file, "r"));
}

char * so_find_steals(char * word, char * pool){
    FILE * file;
    char * ptr;
    size_t size;
    file = open_memstream(&ptr, &size);
    find_steals(root, word, pool, file);
    fclose(file);
    return ptr;
}

void so_free(char * steals){
    free(steals);
}

int main(int argc, char * argv[]){
    int i;
    int sock, connected, bytes_recieved, opt_val = 1;
    struct sockaddr_in server_addr, client_addr;
    int sin_size;

    char send_data[1024], recv_data[1024];
    FILE * out_fp;

    if((sock = socket(AF_INET, SOCK_STREAM, 0)) == -1){
        perror("Error creating socket");
        exit(1);
    }

    if(setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, &opt_val, sizeof(int)) == -1){
        perror("Error setting socket options");
        exit(1);

    }

    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(5000);
    server_addr.sin_addr.s_addr = INADDR_ANY;
    bzero(&(server_addr.sin_zero), 8);

    if(bind(sock, (struct sockaddr *) &server_addr, sizeof(struct sockaddr)) == -1){
        perror("Error binding port");
        exit(1);
    }

    if(listen(sock, 100)){
        perror("Error listening");
        exit(1);
    }

    root = create_tree(fopen("../data/twl06.txt", "r"));

    while(1){
        sin_size = sizeof(struct sockaddr_in);
        connected = accept(sock, (struct sockaddr *) &client_addr, &sin_size);
        //fprintf(stderr, "CONNECTION: %s:%d\n", inet_ntoa(client_addr.sin_addr),ntohs(client_addr.sin_port));

        bytes_recieved = recv(connected, recv_data, 1024, 0);
        if(bytes_recieved == 0){
            close(connected);
            continue;
        }
        if(recv_data[bytes_recieved - 1] == '\n')
            recv_data[bytes_recieved - 1] = '\0';
        else
            recv_data[bytes_recieved] = '\0';

        out_fp = fdopen(connected, "w+");

        if(recv_data[0] == 's'){
            i = 1;
            while(recv_data[i] && recv_data[i] != '_') i++;
            if (recv_data[i] == '_'){
                recv_data[i] = '\0';
                find_steals(root, recv_data + 1, recv_data + i + 1, out_fp);
            }
            else
                find_steals(root, recv_data + 1, 0, out_fp);
        }
        else if(recv_data[0] == 'w')
            fprintf(out_fp, is_word(root, recv_data + 1) ? "YES\n" : "NO\n");

        fclose(out_fp);
        close(connected);

    }

    close(sock);
    return 0;
}

/*
int main(int argc, char * argv[]){
    Node * root;
    int ret;
    int i;

    root = create_tree(fopen("../data/twl06.txt", "r"));

    //ret = is_word(root, "JAY");
    //printf(ret ? "YES\n" : "NO\n");
    //for (i=0;i<1000;i++)
        find_steals(root, "EATORNIS", stdout);
}
*/
