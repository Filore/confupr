Задание 1:

```
local Student(name="Иванов И.И.", group="ИКБО-4-20", age="19") = { 
  age: age, 
  group: group, 
  name: name, 
}; 
 
{ 
   A: [ 
    { groups: [std.join("-", ["ИКБО", std.toString(i), "20"]) for i in std.range(1, 24)] }, 
    {Students: [ 
        Student(), 
        Student("Петров П.П.", "ИКБО-5-20", "18"), 
        Student("Сидоров С.С.", "ИКБО-5-20", "18"), 
        Student("Топорков М.А.", "ИКБО-63-23", "18") 
      ]}, 
    { Subject: "Конфигурационное управление" } 
  ] 
}
```
<img width="817" alt="image" src="https://github.com/user-attachments/assets/02340d2a-59ea-4703-abd3-9d06fda05fb8">


Задание 2:

```
let Prelude = https://prelude.dhall-lang.org/v20.2.0/package.dhall
let generateGroup = λ(i : Natural) → "ИКБО-" ++ Prelude.Natural.show i ++ "-20"

let groups : List Text = Prelude.List.generate 24 Text generateGroup

in  { groups = groups,
      students =
      [ { age = 19, group = "ИКБО-4-20", name = "Иванов И.И." }
      , { age = 18, group = "ИКБО-5-20", name = "Петров П.П." }
      , { age = 18, group = "ИКБО-5-20", name = "Сидоров С.С." }
      , { age = 18, group = "ИКБО-63-23", name = "Топорков М.А." }
      ]
    , subject = "Конфигурационное управление"
 }
```
<img width="983" alt="image" src="https://github.com/user-attachments/assets/6b3f9bb7-ca3f-4f80-a923-22cb034f0a1a">

Задание 3

```
BNF = '''
E = Digit | E Digit
Digit = 0 | 1
'''
```

<img width="983" alt="image" src="https://github.com/user-attachments/assets/e130533f-7097-402c-9ec9-4b9114d682a9">

Задание 4:

```
BNF = '''
E = Pair | E Pair
Pair = ( E ) | { E } | ( ) | { }
'''
```

<img width="983" alt="image" src="https://github.com/user-attachments/assets/bc18a830-18f8-42a9-bf5f-9f221648e448">


Задание 5:

```
BNF = ''' 
E = T EPrime 
EPrime = Op T EPrime |  
T = ~ T | ( E ) | Var 
Op = & | | 
Var = x | y 
'''
```

![image](https://github.com/user-attachments/assets/9201ea98-9121-4ff6-ba01-3a75aaaa73a9)

