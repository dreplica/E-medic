#include <cs50.h>
#include <stdio.h>
void output(void);
int main(void)
{
output();
}
void output(void){
    int n = get_int("Height:");
    for(int i = 0; i<=n; i++){
        for(int j=0; j<=i;j++){
            printf("#");
        }
        printf("\n");
    }
}
