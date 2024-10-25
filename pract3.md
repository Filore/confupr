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

Задание 3

```
BNF = '''
E = 10 | 100 | 11 | 101101 | 000
'''
```

Задание 4:

```
BNF = '''
E = "()" | "{}" | E E | "(" E ")" | "{" E "}"
'''
```

Задание 5:

```
BNF = '''
E = "~" E | E "&" E | E "|" E | "(" E ")" | "x" | "y"
'''
```
