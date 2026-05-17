fn calculate_positive_sum(mut arr: [i32; 5]) -> i32 {
    let mut sum: i32 = 0;
    
    // 结合 for 循环与基本表达式
    for mut i in 0..5 {
        // 结合数组元素访问、条件判断、比较运算
        if arr[i] > 0 {
            // 结合赋值语句和算术运算
            sum = sum + arr[i];
        } else if arr[i] == 0 {
            // 无操作，仅测试 else if 的解析
            sum = sum + 0;
        } else {
            sum = sum - arr[i]; // 将负数取反后相加
        }
    }
    
    // 结合 while 循环和返回值
    while sum > 100 {
        sum = sum - 10;
    }
    
    return sum;
}