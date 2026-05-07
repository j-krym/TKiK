int main() {
    int i = 0;
    int total = 0;
    int state = 2;

    switch (state) {
        case 1:
            total = total + 1;
            break;
        case 2:
            total = total + 2;
            if (total > 1) {
                total = total + 5;
            }
            break;
        default:
            total = total + 10;
    }

    for (i = 0; i < 3; i = i + 1) {
        total = total + i;
    }

    return total;
}
