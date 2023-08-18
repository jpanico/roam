# Creative Brief

Natural language, English for instance, is written for a single species of audience: human readers. It is used to convey ideas from one human to another, and is, by its nature, ambiguous in terms of __formal logic__. Computer programming source code, on the other hand, is written for two species of audience: computers, and human computer programmers (the readers). For the computer, source code is an unambiguous set of instructions that the computer is to carry out. For the human computer programmer, that same source code represents an attempt, by the author, to explain how the source code works and how to use it. For source code to perform its role for humans well, it must be **easily comprehensible** by humans-- humans cannot sensibly use something they can't fully understand.

There is no end to the possible different ways that source code can be written to achieve the exact same result from a computer. The computer doesn't care which possible choice of source code it is given to execute-- it just happily carries out the instructions contained within. But some choices of source code will be radically more comprehensible to human readers than other choices. For instance, consider a very simple programming exercise:

> Write a program that prints out the numbers 1 to 100 (inclusive). If the number is evenly divisible by 3, print __'Fizz'__ instead of the number. If the number is evenly divisible by 5, print __'Buzz'__ instead of the number. If the number is evenly divisible by both 3 and 5, print __'FizzBuzz'__ instead of the number.

The output should look exactly like this: 1,2,Fizz,4,Buzz,Fizz,7,8,Fizz,Buzz,11,Fizz,13,14,FizzBuzz,16,17,Fizz,19,Buzz,Fizz,22,23,Fizz,Buzz,26,Fizz,28,29,FizzBuzz,31,32,Fizz,34,Buzz,Fizz,37,38,Fizz,Buzz,41,Fizz,43,44,FizzBuzz,46,47,Fizz,49,Buzz,Fizz,52,53,Fizz,Buzz,56,Fizz,58,59,FizzBuzz,61,62,Fizz,64,Buzz,Fizz,67,68,Fizz,Buzz,71,Fizz,73,74,FizzBuzz,76,77,Fizz,79,Buzz,Fizz,82,83,Fizz,Buzz,86,Fizz,88,89,FizzBuzz,91,92,Fizz,94,Buzz,Fizz,97,98,Fizz,Buzz

## Solution 1 -- easy to understand

Here is a very easy to understand implementation (in JavaScript). It simply loops through all of the numbers from 1 to 100, checking each number. The reader really only has to understand one thing: that the '%' (modulo) operator returns the remainder of dividing the left hand side by the right hand side. So `( (number % 3) == 0 )` means that `number` is evenly divisible by 3, and  `( (number % 5) == 0 )` means that `number` is evenly divisible by 5. `&&` is the logical AND operator, so `(number % 3) == 0) && (number % 5 == 0)` means that `number` is evenly divisible by both 3 and 5.

### example 1

```javascript
results = []

for (number=1; number<=100; number++) {

    if( ( (number % 3) == 0) && (number % 5 == 0) ) {
        results.push('FizzBuzz')
     }
    else if( number % 3 == 0 ) {
        results.push('Fizz')
    }
    else if( number % 5 == 0 ) {
        results.push('Buzz')
    }
    else {
        results.push(number)
    }
    
}

console.log(`results = ${results}`)
```

## solution 2 (hard to understand)

```javascript
results = ""
FizzBuzz(1)
console.log(`results = ${results}`)

function FizzBuzz(s) {

    if (s > 100) {
        return
    }
    for (let i = 0; i <= 100; i++) {
        if (i == s) {
            stri = i.toString()
            div5 = false
            div3 = false
            if (stri.charAt(stri.length - 1) == '5' || stri.charAt(stri.length - 1) == '0') {
                div5 = true
            }

            gotSum = false
            while (!gotSum) {
                sum = 0
                for (let l = 0; l < stri.length; l++) {
                    v = parseInt(stri[l])
                    sum = sum + v
                }
                sumS = sum.toString()
                if (sumS.length >= 2) {
                    stri = sumS
                } else {
                    if (sum == 3 || sum == 6 || sum == 9) {
                        div3 = true
                    }
                    gotSum = true
                }
            }
            if (div3) {
                results = results.concat(`Fizz`)
            }
            if (div5) {
                results = results.concat(`Buzz`)
            }  
            if (!div3 && !div5) {
                results = results.concat(`${i}`)
            }
            if(i<100) {
                results = results.concat(`,`)
            }
        }
    }
    FizzBuzz(s + 1)
}
```

But crafting code to be comprehensible does not come for free. It requires careful thought, effort, practice and feedback.

So every programmer, whether they know it or not, is making a decision each time they write some code--
