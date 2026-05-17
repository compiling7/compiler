// 数组声明、赋值与元素访问 [cite: 302, 305, 308, 309]
fn program_8_3(mut a:[i32;3]) {
    let mut c:[i32;3];
    c = [1,2,3];
    let mut b:i32=a[0];
    a[0]=1;
    a[1]=a[2]+c[0];
}