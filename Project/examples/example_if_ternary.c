#include<stdio.h>

int max(int a, int b) {
    if (a > b) {
        return a;
    } else if (a == b) {
        return a;
    } else if(a<b) {
        return b;
    }
    else{
        return 0;
    }
}





int main() {
    int x = 10;
    int y = 20;
    int best = max(x, y);
    int result = best > 15 ? 100 : 200;
    printf("best=%d\n%d", result,result+1);
    return result;
}
