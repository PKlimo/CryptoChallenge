#include <stdlib.h> //exit
#include <ctype.h> //isalnum
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>

struct stat sb;
uint8_t *p;
bool debug = true;

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

int score_char(uint8_t znak) {
        if (znak == ' ') return 1;
        else if (isalnum(znak)) return 1;
        else return 0;
}

int score_key_keylen(uint8_t key, int key_len, int offset){
        int score = 0;
        for (off_t len = offset; len < sb.st_size; len+=key_len) //score the buffer for given key and key_len
                score += score_char(p[len] ^ key);
        return score;
}

int score_keylen(int key_len){
        //return score for best key of given key_len
        uint8_t key = 0;
        int score, best_score = 0;
        for (int i = 0; i < 256; i++, key++){
                score = score_key_keylen(key, key_len, 0);
                if (score > best_score)
                        best_score = score;
        }
        return best_score;
}

int find_key_len(int max_key_len) {
        int best_key_len, score, best_score;
        float norm_score, best_norm_score = 0;
        if (debug) printf("length of buffer: %i\n", (int)sb.st_size);

        for (int key_len = 1; key_len <= max_key_len; key_len++) {
                score = score_keylen(key_len);
                norm_score = score / ((float)sb.st_size/key_len);
                if (norm_score > best_norm_score) {
                        best_norm_score = norm_score;
                        best_key_len = key_len;
                        best_score = score;
                }
        }
        if (debug) printf("Score for keylength %i: %i\n", best_key_len ,best_score);
        if (debug) printf("Normalized score for keylength %i: %f\n", best_key_len,best_norm_score);
        if (debug) printf("Size of block for keylength %i: %f\n", best_key_len, (float)sb.st_size / best_key_len);
        return best_key_len;
}

int main (int argc, char *argv[]){
        if (argc < 2) {
                fprintf (stderr, "usage: %s <file>\n", argv[0]);
                exit(EXIT_FAILURE);
        }

        read_into_memory(argv[1]); //fill global pointer (array) p
        int key_len = find_key_len(82);
        printf("Guessed key length: %i\n", key_len);

        uint8_t key = 0, best_key;
        int score, best_score;

        printf("Key: ");

        for (int offset = 0; offset < key_len; offset++){
                best_score = 0;
                for (int i = 0; i < 256; i++, key++){
                        score = score_key_keylen(key, key_len, offset);
                        if (score > best_score) {
                                best_score = score;
                                best_key = key;
                        }
                }
                putchar(best_key);
        }

        putchar('\n');

        free_memory();
        exit(EXIT_SUCCESS);
}
