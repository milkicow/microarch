# CPU Pipeline

## Processor Model

| Parameter | Value |
|-----------|-------|
| Type | Superscalar in-order (in-order issue) |
| Issue width | 2 |
| Instruction Queue | 2 slots |
| Integer pipelines | 2 × (E1 → E2) |
| Memory units | 5 independent, non-pipelined |
| Branch predictor | Ideal (perfect) |

### Stage Latencies

| Instruction type | Stages | Cycles |
|-----------------|--------|--------|
| ALU / Logic / Shift | F → D → E1 → E2 → WB | 5 |
| Load | F → D → E1 → Mem × 3 → WB | 7 |
| Store | F → D → E1 → Mem × 3 | 6 |
| Branch / RET | F → D → E1 | 3 |

### Forwarding (Bypassing)

- **ALU** result available at end of **E2**
- **Load** result available at end of **Mem** (3rd cycle)

---

## Function example:

```cpp
int count_nonzero(const int *arr, int n) {
  int count = 0;
  for (int i = 0; i < n; i++) {
    if (arr[i] == 0)
      break;
    count++;
  }
  return count;
}
```

Instruction trace are collected for next input array:

```cpp
const int arr[5] = {1, 2, 3, 4, 5};
count_nonzero(arr, 5);
```

## AArch64 assembly:

```bash
clang++ -c example.cpp -O1
```

```asm
0000000000000000 <count_nonzero>:
       0: 7100043f     	cmp	w1, #0x1
       4: 5400016b     	b.lt	0x30 <count_nonzero+0x30>
       8: aa0003e8     	mov	x8, x0
       c: d2800000     	mov	x0, #0x0                ; =0
      10: 2a0103e9     	mov	w9, w1
      14: b860790a     	ldr	w10, [x8, x0, lsl #2]
      18: 340000aa     	cbz	w10, 0x2c <count_nonzero+0x2c>
      1c: 91000400     	add	x0, x0, #0x1
      20: eb00013f     	cmp	x9, x0
      24: 54ffff81     	b.ne	0x14 <count_nonzero+0x14>
      28: aa0903e0     	mov	x0, x9
      2c: d65f03c0     	ret
      30: 52800000     	mov	w0, #0x0                ; =0
      34: d65f03c0     	ret
```

## Pipeline diagram

|                            | 1     | 2      | 3  | 4      | 5  | 6      | 7  | 8      | 9  | 10     | 11  | 12  | 13 | 14     | 15 | 16     | 17 | 18     | 19  | 20  | 21 | 22     | 23 | 24     | 25 | 26     | 27  | 28  | 29 | 30     | 31 | 32     | 33 | 34     | 35  | 36  | 37 | 38     | 39 | 40     | 41 | 42     | 43  | 44  | 45 |
|----------------------------|-------|--------|----|--------|----|--------|----|--------|----|--------|-----|-----|----|--------|----|--------|----|--------|-----|-----|----|--------|----|--------|----|--------|-----|-----|----|--------|----|--------|----|--------|-----|-----|----|--------|----|--------|----|--------|-----|-----|----|
| cmp w1, #0x1               | FETCH | DECODE | E1 | E2     | WB |        |    |        |    |        |     |     |    |        |    |        |    |        |     |     |    |        |    |        |    |        |     |     |    |        |    |        |    |        |     |     |    |        |    |        |    |        |     |     |    |
| b.lt 0x30 <count_nonzero+0x30>     | FETCH | DECODE | -  | -      | E1 |        |    |        |    |        |     |     |    |        |    |        |    |        |     |     |    |        |    |        |    |        |     |     |    |        |    |        |    |        |     |     |    |        |    |        |    |        |     |     |    |
| mov x8, x0                 | -     | FETCH  | -  | DECODE | E1 | E2     | WB |        |    |        |     |     |    |        |    |        |    |        |     |     |    |        |    |        |    |        |     |     |    |        |    |        |    |        |     |     |    |        |    |        |    |        |     |     |    |
| mov x0, #0x0               | -     | FETCH  | -  | -      | -  | DECODE | E1 | E2     | WB |        |     |     |    |        |    |        |    |        |     |     |    |        |    |        |    |        |     |     |    |        |    |        |    |        |     |     |    |        |    |        |    |        |     |     |    |
| mov w9, w1                 | -     | -      | -  | FETCH  | -  | DECODE | E1 | E2     | WB |        |     |     |    |        |    |        |    |        |     |     |    |        |    |        |    |        |     |     |    |        |    |        |    |        |     |     |    |        |    |        |    |        |     |     |    |
| ldr w10, [x8, x0, lsl #2]  | -     | -      | -  | -      | -  | FETCH  | -  | DECODE | E1 | MEM    | MEM | MEM | WB |        |    |        |    |        |     |     |    |        |    |        |    |        |     |     |    |        |    |        |    |        |     |     |    |        |    |        |    |        |     |     |    |
| cbz w10, 0x2c <count_nonzero+0x2c> | -     | -      | -  | -      | -  | FETCH  | -  | DECODE | -  | -      | -   | -   | E1 |        |    |        |    |        |     |     |    |        |    |        |    |        |     |     |    |        |    |        |    |        |     |     |    |        |    |        |    |        |     |     |    |
| add x0, x0, #0x1           | -     | -      | -  | -      | -  | -      | -  | FETCH  | -  | DECODE | -   | -   | E1 | E2     | WB |        |    |        |     |     |    |        |    |        |    |        |     |     |    |        |    |        |    |        |     |     |    |        |    |        |    |        |     |     |    |
| cmp x9, x0                 | -     | -      | -  | -      | -  | -      | -  | FETCH  | -  | -      | -   | -   | -  | DECODE | E1 | E2     | WB |        |     |     |    |        |    |        |    |        |     |     |    |        |    |        |    |        |     |     |    |        |    |        |    |        |     |     |    |
| b.ne 0x14 <count_nonzero+0x14>     | -     | -      | -  | -      | -  | -      | -  | -      | -  | FETCH  | -   | -   | -  | DECODE | -  | -      | E1 |        |     |     |    |        |    |        |    |        |     |     |    |        |    |        |    |        |     |     |    |        |    |        |    |        |     |     |    |
| ldr w10, [x8, x0, lsl #2]  | -     | -      | -  | -      | -  | -      | -  | -      | -  | -      | -   | -   | -  | FETCH  | -  | DECODE | E1 | MEM    | MEM | MEM | WB |        |    |        |    |        |     |     |    |        |    |        |    |        |     |     |    |        |    |        |    |        |     |     |    |
| cbz w10, 0x2c <count_nonzero+0x2c> | -     | -      | -  | -      | -  | -      | -  | -      | -  | -      | -   | -   | -  | FETCH  | -  | -      | -  | DECODE | -   | -   | E1 |        |    |        |    |        |     |     |    |        |    |        |    |        |     |     |    |        |    |        |    |        |     |     |    |
| add x0, x0, #0x1           | -     | -      | -  | -      | -  | -      | -  | -      | -  | -      | -   | -   | -  | -      | -  | FETCH  | -  | DECODE | -   | -   | E1 | E2     | WB |        |    |        |     |     |    |        |    |        |    |        |     |     |    |        |    |        |    |        |     |     |    |
| cmp x9, x0                 | -     | -      | -  | -      | -  | -      | -  | -      | -  | -      | -   | -   | -  | -      | -  | -      | -  | FETCH  | -   | -   | -  | DECODE | E1 | E2     | WB |        |     |     |    |        |    |        |    |        |     |     |    |        |    |        |    |        |     |     |    |
| b.ne 0x14 <count_nonzero+0x14>     | -     | -      | -  | -      | -  | -      | -  | -      | -  | -      | -   | -   | -  | -      | -  | -      | -  | FETCH  | -   | -   | -  | DECODE | -  | -      | E1 |        |     |     |    |        |    |        |    |        |     |     |    |        |    |        |    |        |     |     |    |
| ldr w10, [x8, x0, lsl #2]  | -     | -      | -  | -      | -  | -      | -  | -      | -  | -      | -   | -   | -  | -      | -  | -      | -  | -      | -   | -   | -  | FETCH  | -  | DECODE | E1 | MEM    | MEM | MEM | WB |        |    |        |    |        |     |     |    |        |    |        |    |        |     |     |    |
| cbz w10, 0x2c <count_nonzero+0x2c> | -     | -      | -  | -      | -  | -      | -  | -      | -  | -      | -   | -   | -  | -      | -  | -      | -  | -      | -   | -   | -  | FETCH  | -  | -      | -  | DECODE | -   | -   | E1 |        |    |        |    |        |     |     |    |        |    |        |    |        |     |     |    |
| add x0, x0, #0x1           | -     | -      | -  | -      | -  | -      | -  | -      | -  | -      | -   | -   | -  | -      | -  | -      | -  | -      | -   | -   | -  | -      | -  | FETCH  | -  | DECODE | -   | -   | E1 | E2     | WB |        |    |        |     |     |    |        |    |        |    |        |     |     |    |
| cmp x9, x0                 | -     | -      | -  | -      | -  | -      | -  | -      | -  | -      | -   | -   | -  | -      | -  | -      | -  | -      | -   | -   | -  | -      | -  | -      | -  | FETCH  | -   | -   | -  | DECODE | E1 | E2     | WB |        |     |     |    |        |    |        |    |        |     |     |    |
| b.ne 0x14 <count_nonzero+0x14>     | -     | -      | -  | -      | -  | -      | -  | -      | -  | -      | -   | -   | -  | -      | -  | -      | -  | -      | -   | -   | -  | -      | -  | -      | -  | FETCH  | -   | -   | -  | DECODE | -  | -      | E1 |        |     |     |    |        |    |        |    |        |     |     |    |
| ldr w10, [x8, x0, lsl #2]  | -     | -      | -  | -      | -  | -      | -  | -      | -  | -      | -   | -   | -  | -      | -  | -      | -  | -      | -   | -   | -  | -      | -  | -      | -  | -      | -   | -   | -  | FETCH  | -  | DECODE | E1 | MEM    | MEM | MEM | WB |        |    |        |    |        |     |     |    |
| cbz w10, 0x2c <count_nonzero+0x2c> | -     | -      | -  | -      | -  | -      | -  | -      | -  | -      | -   | -   | -  | -      | -  | -      | -  | -      | -   | -   | -  | -      | -  | -      | -  | -      | -   | -   | -  | FETCH  | -  | -      | -  | DECODE | -   | -   | E1 |        |    |        |    |        |     |     |    |
| add x0, x0, #0x1           | -     | -      | -  | -      | -  | -      | -  | -      | -  | -      | -   | -   | -  | -      | -  | -      | -  | -      | -   | -   | -  | -      | -  | -      | -  | -      | -   | -   | -  | -      | -  | FETCH  | -  | DECODE | -   | -   | E1 | E2     | WB |        |    |        |     |     |    |
| cmp x9, x0                 | -     | -      | -  | -      | -  | -      | -  | -      | -  | -      | -   | -   | -  | -      | -  | -      | -  | -      | -   | -   | -  | -      | -  | -      | -  | -      | -   | -   | -  | -      | -  | -      | -  | FETCH  | -   | -   | -  | DECODE | E1 | E2     | WB |        |     |     |    |
| b.ne 0x14 <count_nonzero+0x14>     | -     | -      | -  | -      | -  | -      | -  | -      | -  | -      | -   | -   | -  | -      | -  | -      | -  | -      | -   | -   | -  | -      | -  | -      | -  | -      | -   | -   | -  | -      | -  | -      | -  | FETCH  | -   | -   | -  | DECODE | -  | -      | E1 |        |     |     |    |
| ldr w10, [x8, x0, lsl #2]  | -     | -      | -  | -      | -  | -      | -  | -      | -  | -      | -   | -   | -  | -      | -  | -      | -  | -      | -   | -   | -  | -      | -  | -      | -  | -      | -   | -   | -  | -      | -  | -      | -  | -      | -   | -   | -  | FETCH  | -  | DECODE | E1 | MEM    | MEM | MEM | WB |
| cbz w10, 0x2c <count_nonzero+0x2c> | -     | -      | -  | -      | -  | -      | -  | -      | -  | -      | -   | -   | -  | -      | -  | -      | -  | -      | -   | -   | -  | -      | -  | -      | -  | -      | -   | -   | -  | -      | -  | -      | -  | -      | -   | -   | -  | FETCH  | -  | -      | -  | DECODE | -   | -   | E1 |
| ret                        | -     | -      | -  | -      | -  | -      | -  | -      | -  | -      | -   | -   | -  | -      | -  | -      | -  | -      | -   | -   | -  | -      | -  | -      | -  | -      | -   | -   | -  | -      | -  | -      | -  | -      | -   | -   | -  | -      | -  | FETCH  | -  | DECODE | -   | -   | E1 |
|                            |       |        |    |        |    |        |    |        |    |        |     |     |    |        |    |        |    |        |     |     |    |        |    |        |    |        |     |     |    |        |    |        |    |        |     |     |    |        |    |        |    |        |     |     |    |
|                            |       |        |    |        |    |        |    |        |    |        |     |     |    |        |    |        |    |        |     |     |    |        |    |        |    |        |     |     |    |        |    |        |    |        |     |     |    |        |    |        |    |        |     |     |    |

## Discussion

In CPU model with issue width == 2, program execution takes **45** cycles

For CPU with issue width == 4:
Prologue will be:

|                             | 1     | 2      | 3      | 4  | 5   | 6   | 7   |
|-----------------------------|-------|--------|--------|----|-----|-----|-----|
| cmp	w1, #0x1              | FETCH | DECODE | E1     | E2 | WB  |     |     |
| b.lt	0x30 <ltmp0+0x30>     | FETCH | DECODE | -      | -  | E1  |     |     |
| mov	x8, x0                | FETCH | DECODE | -      | -  | E1  | E2  | W   |
| mov	x0, #0x0              | FETCH | DECODE | -      | -  | E1  | E2  | W   |
| mov	w9, w1                | -     | FETCH  | -      | DECODE | E1 | E2  | WB  |     |
| ldr	w10, [x8, x0, lsl #2] | -     | FETCH  | -      | - | - | DECODE | E1 |

So CBZ can use result of LDR on 2 cycles earlier. **45** -> **43**

Loop body:

Critical path defined by data flow: **LDR** -> **CBZ** -> **ADD** -> **CMP** -> **BNE** -> **LDR** (next body) -> ...

Width of pipeline can not change it.

$$Speedup = \frac{45}{43} \approx \mathbf{1.047} \Rightarrow \mathbf{+4.7}\%$$