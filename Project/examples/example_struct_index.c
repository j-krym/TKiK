struct Point {
    int x;
    int y;
};

int main() {
    struct Point p;
    p.x = 3;
    p.y = 4;

    int values[5];
    values[0] = 1;
    values[1] = 2;
    values[2] = 3;
    values[3] = 4;
    values[4] = 5;

    int sum = values[p.x] + values[p.y - 1];
    int threshold = (sum > 7 && p.x < p.y) ? 42 : 7;

    printf("sum=%d threshold=%d\n", sum, threshold);
    return threshold;
}
