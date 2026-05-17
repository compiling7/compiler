fn program_5_1(mut n:i32) {
    // while循环 [cite: 209, 210, 211]
    while n>0 {
        n=n-1;
    }
}

fn program_5_2(mut n:i32) {
    // for..in 循环及可迭代结构 (表达式..表达式) [cite: 214, 215, 216]
    for mut i in 1..n+1 {
        n=n-1;
    }
}