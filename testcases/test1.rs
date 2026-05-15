// 测试用例1: 基本函数声明和变量声明
fn add(a: i32, b: i32) -> i32 {
    return a + b;
}

fn main() -> i32 {
    let x: i32 = 10;
    let mut y: i32 = 5;
    y = x + 20;
    let result: i32 = add(x, y);
    return result;
}