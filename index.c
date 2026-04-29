#include<stdio.h>
#include<stdlib.h>
#define maxsize 100
typedef  int datatype;
typedef void (*step_callback)(int* arr, int n, int i, int j);
step_callback g_callback = NULL;

void set_callback(step_callback cb) {
    g_callback = cb;
}

struct tuple {
    int x;
    int y;
};
void set_random_seed(unsigned int seed) {
    srand(seed);
}
int random_in_range(struct tuple range) {
    return rand() % (range.y - range.x + 1) + range.x;
}

void ACM_maopao(datatype a[], int n) {
    for (int i = 0; i < n - 1; i++) {
        for (int j = 0; j < n - 1 - i; j++) {
            if (a[j] > a[j + 1]) {
                int temp = a[j];
                a[j] = a[j + 1];
                a[j + 1] = temp;
                if (g_callback) g_callback(a, n, j, j + 1);
            }
        }
    }
}
void ACM_xuanze(datatype a[], int n) {
    for (int i = 0; i < n - 1; i++) {
        int min = i;
        for (int j = i + 1; j < n; j++) {
            if (a[j] < a[min]) {
                min = j;
            }
        }
        if (min != i) {
            int temp = a[i];
            a[i] = a[min];
            a[min] = temp;
            if (g_callback) g_callback(a, n, i, min);     
        }
    }
}
void ACM_kuaisu(datatype a[], int left, int right) {
    if (left < right) {
        int i = left, j = right, pivot = a[left];
        while (i < j) {
            while (i < j && a[j] >= pivot) j--;
            if (i < j) {
                a[i] = a[j];
                if (g_callback) g_callback(a, right - left + 1, i, j); 
                i++;
            }
            while (i < j && a[i] <= pivot) i++;
            if (i < j) {
                a[j] = a[i];
                if (g_callback) g_callback(a, right - left + 1, j, i);
                j--;
            }
        }
        a[i] = pivot;
        if (g_callback) g_callback(a, right - left + 1, i, i); 
        ACM_kuaisu(a, left, i - 1);
        ACM_kuaisu(a, i + 1, right);
    }
}
void ACM_insert(datatype a[], int n) {
    for (int i = 1; i < n; i++) {
        int key = a[i];
        int j = i - 1;
        while (j >= 0 && a[j] > key) {
            a[j + 1] = a[j];
            if (g_callback) g_callback(a, n, j + 1, j);     
            j--;
        }
        a[j + 1] = key;
        if (g_callback) g_callback(a, n, j + 1, i);         
    }
}
int main(){
    int a[maxsize];
    int n;
    printf("请输入数组的长度：");
    scanf("%d",&n);
    printf("请输入随机数的范围：");
    struct tuple range;
    scanf("%d%d",&range.x,&range.y);
    for (int i = 0; i < n; i++){
        a[i] = random_in_range(range);
    }
    printf("排序前的数组为：");
    for (int i = 0; i < n; i++){
        printf("%d ",a[i]);
    }
    printf("\n");
    int choice;
    printf("请选择排序算法：1.冒泡排序 2.选择排序 3.快速排序 4.插入排序\n");
    scanf("%d",&choice);
    switch (choice)
    {
    case 1:
        ACM_maopao(a,n);
        break;
    case 2:
        ACM_xuanze(a,n);
        break;
    case 3:
        ACM_kuaisu(a,0,n-1);
        break;
    case 4:
        ACM_insert(a,n);
        break;
    default:
        break;
    }
    printf("排序后的数组为：");
    for (int i = 0; i < n; i++){
        printf("%d ",a[i]);
    }
    return 0;
}