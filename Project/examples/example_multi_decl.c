int main() {
    int a = 1, b = 2, c = 3;
    int count = 0;
    int data[3];
    data[0] = a;
    data[1] = b;
    data[2] = c;

    if (a < b || b < c) {
        count = count + 1;
    } else {
        count = count + 2;
    }

    count = count + (data[0] == 1 ? 10 : 20);

    ++a;
    b--;
    int values = a + b + c;

    printf("count=%d values=%d\n", count, values);
    return values;
}
