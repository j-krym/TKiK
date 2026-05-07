#include<stdio.h>

int max(int a, int b) {
    if (a > b) {
        return a;
    } else if (a == b) {
        return a;
    } else {
        return b;
    }
}

int main() {
    int x = 10;
    int y = 20;
    int best = max(x, y);
    int result = best > 15 ? 100 : 200;
    printf("best=%d\n", result);
    return result;
}
