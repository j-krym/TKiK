int main() {
    int score = 85;
    int grade = score > 90 ? 1 : score > 75 ? 2 : 3;
    printf("grade=%d\n", grade);
    return grade;
}
