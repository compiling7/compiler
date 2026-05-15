// 测试用例2: 条件语句和循环语句
fn fibonacci(n: i32) -> i32 {
    if n <= 1 {
        return n;
    }
    let mut a: i32 = 0;
    let mut b: i32 = 1;
    let mut i: i32 = 2;
    while i <= n {
        let temp: i32 = a + b;
        a = b;
        b = temp;
        i = i + 1;
    }
    return b;
}

fn gcd(a: i32, b: i32) -> i32 {
    let mut x: i32 = a;
    let mut y: i32 = b;
    while y != 0 {
        let t: i32 = y;
        y = x - (x / y) * y;
        x = t;
    }
    return x;
}