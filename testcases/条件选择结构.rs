// 完整的 if-else if-else 分支结构 [cite: 184, 185, 186, 187, 188, 189, 190, 191, 192]
fn program_4_3(a:i32) -> i32 {
    if a>0 {
        return a+1;
    } else if a<0 {
        return a-1;
    } else {
        return 0;
    }
}