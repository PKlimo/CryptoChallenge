#include <string.h> //atoi, strlen
#include <stddef.h> //size_t
#include <stdio.h> //printf
#include <stdlib.h> //exit
#include <stdbool.h> //bool

bool debug = true;

int main (int argc, char *argv[]){
        if (argc < 3) {
                fprintf (stderr, "usage: %s N \"string\"\n", argv[0]);
                exit(EXIT_FAILURE);
        }
        size_t n = atoi(argv[1]);
        size_t len = strlen(argv[2]);
        if ( (n<len) || (n>256) ) {
                fprintf(stderr, "N must be from interval <%zu,256>", len);
                exit(EXIT_FAILURE);
        }

        if (debug) fprintf(stderr, "Padding length: %zu\nString length: %zu\nString: %s\n", n, len, argv[2]);
        char diff = n - len;
        if (debug) fprintf(stderr, "Number of padding bytes: %i\n", diff);
        char *nstr;
        nstr = (char *)calloc(n+1,sizeof(char));
        strcpy(nstr, argv[2]);
        memset(nstr+len, diff, diff*sizeof(char));
        printf("%s", nstr);
        return 0;
}
