int sum_to_n(int n) { 
    int i = 0;
    int total = 0;
    for (i = 0; i < n; i = i + 1) {
        total = total + i;
    }
    if(i == 1){
        i = 1;
    }
    else if(i==2){
        i=2;
    }
    else
    
    {
        i = 3;
    }
    return total;
}

int main() {
    int result = sum_to_n(5);
    printf("%d\n", result);
    return 0;
}
