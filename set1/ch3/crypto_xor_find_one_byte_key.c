#include <stdlib.h> //exit
#include <ctype.h> //isalnum
#include <stdint.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>

struct stat sb;
uint8_t *p;

void read_into_memory(char *fname) {
        int fd = open (fname, O_RDONLY);
        if (fd == -1) {
                perror ("open");
                exit(EXIT_FAILURE);
        }
        if (fstat (fd, &sb) == -1) {
                perror ("fstat");
                exit(EXIT_FAILURE);
        }
        if (!S_ISREG (sb.st_mode)) {
                fprintf (stderr, "%s is not a file\n", fname);
                exit(EXIT_FAILURE);
        }
        p = mmap (0, sb.st_size, PROT_READ, MAP_SHARED, fd, 0);
        if (p == MAP_FAILED) {
                perror ("mmap");
                exit(EXIT_FAILURE);
        }
        if (close (fd) == -1) {
                perror ("close");
                exit(EXIT_FAILURE);
        }
}

void free_memory() {
        if (munmap (p, sb.st_size) == -1) {
                perror ("munmap");
                exit(EXIT_FAILURE);
        }
}

int main (int argc, char *argv[]){
        if (argc < 2) {
                fprintf (stderr, "usage: %s <file>\n", argv[0]);
                exit(EXIT_FAILURE);
        }

        read_into_memory(argv[1]);


        uint8_t key, best_key, dec;
        int i, score, best_score = 0;

        for (key = 0, i = 0; i < 256; key++, i++){
                score = 0;
                for (off_t len = 0; len < sb.st_size; len++) {
                        dec = p[len] ^ key;
                        if (dec == ' ') score += 5;
                        else if (isalnum(dec)) score += 1;
                }
                if (score > best_score) {
                        best_score = score;
                        best_key = key;
                }
        }
        printf("%i;%c;", best_score, best_key);
        for (off_t len = 0; len < sb.st_size; len++) putchar(p[len]^best_key);
        putchar('\n');

        free_memory();
        exit(EXIT_SUCCESS);
}
