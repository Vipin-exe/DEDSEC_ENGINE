#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_TREE_HT 256
#define CHUNK_SIZE 4096 // 4KB Stream Buffer for large file handling

/* --- Data Structures --- */
struct MinHeapNode {
    char data;
    unsigned freq;
    struct MinHeapNode *left, *right;
};

struct MinHeap {
    unsigned size;
    unsigned capacity;
    struct MinHeapNode **array;
};

/* --- Node & Heap Utility Functions --- */
struct MinHeapNode* newNode(char data, unsigned freq) {
    struct MinHeapNode* temp = (struct MinHeapNode*)malloc(sizeof(struct MinHeapNode));
    temp->left = temp->right = NULL;
    temp->data = data;
    temp->freq = freq;
    return temp;
}

struct MinHeap* createMinHeap(unsigned capacity) {
    struct MinHeap* minHeap = (struct MinHeap*)malloc(sizeof(struct MinHeap));
    minHeap->size = 0;
    minHeap->capacity = capacity;
    minHeap->array = (struct MinHeapNode**)malloc(minHeap->capacity * sizeof(struct MinHeapNode*));
    return minHeap;
}

void swapMinHeapNode(struct MinHeapNode** a, struct MinHeapNode** b) {
    struct MinHeapNode* t = *a;
    *a = *b;
    *b = t;
}

void minHeapify(struct MinHeap* minHeap, int idx) {
    int smallest = idx;
    int left = 2 * idx + 1;
    int right = 2 * idx + 2;

    if (left < minHeap->size && minHeap->array[left]->freq < minHeap->array[smallest]->freq)
        smallest = left;

    if (right < minHeap->size && minHeap->array[right]->freq < minHeap->array[smallest]->freq)
        smallest = right;

    if (smallest != idx) {
        swapMinHeapNode(&minHeap->array[smallest], &minHeap->array[idx]);
        minHeapify(minHeap, smallest);
    }
}

int isSizeOne(struct MinHeap* minHeap) {
    return (minHeap->size == 1);
}

struct MinHeapNode* extractMin(struct MinHeap* minHeap) {
    struct MinHeapNode* temp = minHeap->array[0];
    minHeap->array[0] = minHeap->array[minHeap->size - 1];
    --minHeap->size;
    minHeapify(minHeap, 0);
    return temp;
}

void insertMinHeap(struct MinHeap* minHeap, struct MinHeapNode* minHeapNode) {
    ++minHeap->size;
    int i = minHeap->size - 1;
    while (i && minHeapNode->freq < minHeap->array[(i - 1) / 2]->freq) {
        minHeap->array[i] = minHeap->array[(i - 1) / 2];
        i = (i - 1) / 2;
    }
    minHeap->array[i] = minHeapNode;
}

void buildMinHeap(struct MinHeap* minHeap) {
    int n = minHeap->size - 1;
    for (int i = (n - 1) / 2; i >= 0; --i)
        minHeapify(minHeap, i);
}

int isLeaf(struct MinHeapNode* root) {
    return !(root->left) && !(root->right);
}

struct MinHeap* createAndBuildMinHeap(char data[], int freq[], int size) {
    struct MinHeap* minHeap = createMinHeap(size);
    for (int i = 0; i < size; ++i)
        minHeap->array[i] = newNode(data[i], freq[i]);
    minHeap->size = size;
    buildMinHeap(minHeap);
    return minHeap;
}

/* --- Tree Construction --- */
struct MinHeapNode* buildHuffmanTree(char data[], int freq[], int size) {
    struct MinHeapNode *left, *right, *top;
    struct MinHeap* minHeap = createAndBuildMinHeap(data, freq, size);

    while (!isSizeOne(minHeap)) {
        left = extractMin(minHeap);
        right = extractMin(minHeap);
        top = newNode('$', left->freq + right->freq);
        top->left = left;
        top->right = right;
        insertMinHeap(minHeap, top);
    }
    return extractMin(minHeap);
}

/* --- Store Codes in Dictionary --- */
char codes[256][MAX_TREE_HT];

void storeCodes(struct MinHeapNode* root, int arr[], int top) {
    if (root->left) {
        arr[top] = 0;
        storeCodes(root->left, arr, top + 1);
    }
    if (root->right) {
        arr[top] = 1;
        storeCodes(root->right, arr, top + 1);
    }
    if (isLeaf(root)) {
        int i;
        for (i = 0; i < top; ++i) {
            codes[(unsigned char)root->data][i] = arr[i] ? '1' : '0';
        }
        codes[(unsigned char)root->data][i] = '\0';
    }
}

/* --- Compress Function (Encryption) --- */
void compressFile(const char *inputFile, const char *outputFile) {
    FILE *in = fopen(inputFile, "rb");
    if (!in) { printf("Error opening input file.\n"); return; }

    int freq[256] = {0};
    int total_chars = 0;
    
    unsigned char buffer_chunk[CHUNK_SIZE];
    size_t bytes_read;

    // First Pass: Read file in 4KB chunks to calculate frequency
    while ((bytes_read = fread(buffer_chunk, 1, CHUNK_SIZE, in)) > 0) {
        for (size_t i = 0; i < bytes_read; i++) {
            freq[buffer_chunk[i]]++;
            total_chars++;
        }
    }

    int unique_chars = 0;
    for (int i = 0; i < 256; i++) {
        if (freq[i] > 0) unique_chars++;
    }

    char *dataArr = (char*)malloc(unique_chars * sizeof(char));
    int *freqArr = (int*)malloc(unique_chars * sizeof(int));
    int index = 0;
    for (int i = 0; i < 256; i++) {
        if (freq[i] > 0) {
            dataArr[index] = (char)i;
            freqArr[index] = freq[i];
            index++;
        }
    }

    struct MinHeapNode* root = buildHuffmanTree(dataArr, freqArr, unique_chars);
    int arr[MAX_TREE_HT], top = 0;
    
    memset(codes, 0, sizeof(codes));
    storeCodes(root, arr, top);

    FILE *out = fopen(outputFile, "wb");
    if (!out) { printf("Error opening output file.\n"); fclose(in); return; }
    
    // Write DedSec Header for UI rendering
    const char *header = "DEDSEC_ENCRYPTED_PACKAGE\n";
    fwrite(header, 1, strlen(header), out);

    fwrite(&unique_chars, sizeof(int), 1, out);
    for (int i = 0; i < unique_chars; i++) {
        fwrite(&dataArr[i], sizeof(char), 1, out);
        fwrite(&freqArr[i], sizeof(int), 1, out);
    }

    // Rewind input file for the second pass
    fseek(in, 0, SEEK_SET);
    
    unsigned char bit_container = 0;
    int bits_filled = 0;
    
    // Second Pass: Read file in 4KB chunks to encode and bit-pack
    while ((bytes_read = fread(buffer_chunk, 1, CHUNK_SIZE, in)) > 0) {
        for (size_t k = 0; k < bytes_read; k++) {
            unsigned char current_character = buffer_chunk[k];
            char *strCode = codes[current_character];
            
            for (int i = 0; strCode[i] != '\0'; i++) {
                bit_container = bit_container << 1; 
                if (strCode[i] == '1') {
                    bit_container = bit_container | 1;
                }
                bits_filled++;
                
                // Flush to disk immediately when a byte is full
                if (bits_filled == 8) {
                    fwrite(&bit_container, 1, 1, out);
                    bit_container = 0;
                    bits_filled = 0;
                }
            }
        }
    }
    
    // Flush remaining bits
    if (bits_filled > 0) {
        bit_container = bit_container << (8 - bits_filled);
        fwrite(&bit_container, 1, 1, out);
    }

    printf("DedSec Engine: Target successfully compressed and streamed to disk.\n");
    fclose(in);
    fclose(out);
    free(dataArr);
    free(freqArr);
}

/* --- Decompress Function (Decryption) --- */
void decompressFile(const char *inputFile, const char *outputFile) {
    FILE *in = fopen(inputFile, "rb");
    if (!in) { printf("Error opening compressed file.\n"); return; }

    FILE *out = fopen(outputFile, "wb");
    if (!out) { printf("Error opening output file.\n"); fclose(in); return; }

    // Read and verify the DedSec Header
    char expected_header[] = "DEDSEC_ENCRYPTED_PACKAGE\n";
    char read_header[30] = {0};
    fread(read_header, 1, strlen(expected_header), in);
    
    if (strcmp(read_header, expected_header) != 0) {
        printf("CRITICAL ERROR: Not a valid DedSec Encrypted Package.\n");
        fclose(in); fclose(out); return;
    }

    // Read the frequency dictionary
    int unique_chars;
    fread(&unique_chars, sizeof(int), 1, in);

    char *dataArr = (char*)malloc(unique_chars * sizeof(char));
    int *freqArr = (int*)malloc(unique_chars * sizeof(int));
    int total_chars = 0;

    for (int i = 0; i < unique_chars; i++) {
        fread(&dataArr[i], sizeof(char), 1, in);
        fread(&freqArr[i], sizeof(int), 1, in);
        total_chars += freqArr[i]; 
    }

    // Rebuild the Huffman Tree
    struct MinHeapNode* root = buildHuffmanTree(dataArr, freqArr, unique_chars);
    struct MinHeapNode* current = root;

    unsigned char bit_container;
    int decoded_chars = 0;

    // Decode the binary data
    while (fread(&bit_container, 1, 1, in) > 0 && decoded_chars < total_chars) {
        for (int i = 7; i >= 0; i--) {
            int bit = (bit_container >> i) & 1;

            if (bit == 0) current = current->left;
            else current = current->right;

            if (isLeaf(current)) {
                fwrite(&(current->data), 1, 1, out);
                decoded_chars++;
                current = root; 

                if (decoded_chars == total_chars) break; 
            }
        }
    }

    printf("DedSec Engine: File successfully decrypted and restored.\n");
    fclose(in);
    fclose(out);
    free(dataArr);
    free(freqArr);
}

/* --- Main Engine Controller --- */
int main(int argc, char *argv[]) {
    if (argc < 4) {
        printf("Usage: %s <compress/decompress> <input_file> <output_file>\n", argv[0]);
        return 1;
    }

    if (strcmp(argv[1], "compress") == 0) {
        compressFile(argv[2], argv[3]);
    } else if (strcmp(argv[1], "decompress") == 0) {
        decompressFile(argv[2], argv[3]);
    } else {
        printf("Invalid command.\n");
    }

    return 0;
}
