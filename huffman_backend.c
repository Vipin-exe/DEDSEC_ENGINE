#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_TREE_HT 256

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

/* --- Compress Function --- */
void compressFile(const char *inputFile, const char *outputFile) {
    FILE *in = fopen(inputFile, "r");
    if (!in) { printf("Error opening input file.\n"); return; }

    int freq[256] = {0};
    char ch;
    int total_chars = 0;
    while (fread(&ch, 1, 1, in)) {
        freq[(unsigned char)ch]++;
        total_chars++;
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
    
    fwrite(&unique_chars, sizeof(int), 1, out);
    for (int i = 0; i < unique_chars; i++) {
        fwrite(&dataArr[i], sizeof(char), 1, out);
        fwrite(&freqArr[i], sizeof(int), 1, out);
    }

    fseek(in, 0, SEEK_SET);
    
    unsigned char buffer = 0;
    int bits_filled = 0;
    
    while (fread(&ch, 1, 1, in)) {
        char *strCode = codes[(unsigned char)ch];
        for (int i = 0; strCode[i] != '\0'; i++) {
            if (strCode[i] == '1') {
                buffer |= (1 << (7 - bits_filled));
            }
            bits_filled++;
            if (bits_filled == 8) {
                fwrite(&buffer, 1, 1, out);
                buffer = 0;
                bits_filled = 0;
            }
        }
    }
    if (bits_filled > 0) {
        fwrite(&buffer, 1, 1, out);
    }

    printf("SUCCESS! Compression completed.\n");
    fclose(in);
    fclose(out);
    free(dataArr);
    free(freqArr);
}

int main(int argc, char *argv[]) {
    if (argc < 4) {
        printf("Usage: %s compress <input_file> <output_file>\n", argv[0]);
        return 1;
    }

    if (strcmp(argv[1], "compress") == 0) {
        compressFile(argv[2], argv[3]);
    } else {
        printf("Invalid command.\n");
    }

    return 0;
}