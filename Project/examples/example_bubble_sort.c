#include <stdio.h>

void bubble_sort(int arr[], int n) {
    int i, j, temp;

    for (i = 0; i < n - 1; i++) {
        for (j = 0; j < n - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
            }
        }
    }
}

void print_array(int arr[], int n) {
    int i;

    for (i = 0; i < n; i++) {
        printf("%d ", arr[i]);
    }

    printf("\n");
}

int main() {
    int values[8];

    values[0] = 64;
    values[1] = 34;
    values[2] = 25;
    values[3] = 12;
    values[4] = 22;
    values[5] = 11;
    values[6] = 90;
    values[7] = 5;

    printf("Before sorting:\n");
    print_array(values, 8);

    bubble_sort(values, 8);

    printf("After sorting:\n");
    print_array(values, 8);

    return 0;
}