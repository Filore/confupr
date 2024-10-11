Задание 1:

```
grep '.*' /etc/passwd | cut -d: -f1 | sort
```

![telegram-cloud-photo-size-2-5436289455901240425-y](https://github.com/user-attachments/assets/64e34a3b-8de4-41ad-b26d-57e747dc92a1)

Задание 2:
```
awk '{print $2, $1}' /etc/protocols | sort -nr | head -n 5
```

![telegram-cloud-photo-size-2-5436289455901240428-y](https://github.com/user-attachments/assets/1222ae51-e1d9-4b0a-8159-6e9600659aa6)


Задание 3:

![telegram-cloud-photo-size-2-5436289455901240472-x](https://github.com/user-attachments/assets/8c3ad64c-38f2-410f-b9a8-3e1629bef643)


![telegram-cloud-photo-size-2-5436289455901240471-y](https://github.com/user-attachments/assets/c2cdf543-1be2-48b6-83d7-dddcbd9545c5)

Задание 4:

```
#!/bin/bash

file="$1"

id=$(grep -o -E '\b[a-zA-Z]*\b' "$file" | sort -u)
```

```
grep -oE '\b[a-zA-Z_][a-zA-Z0-9_]*\b' hello.c | grep -vE '\b(int|void|return|if|else|for|while|include|stdio)\b' | sort | uniq
```

![telegram-cloud-photo-size-2-5436289455901240506-y](https://github.com/user-attachments/assets/2c67948b-daad-4375-8e4b-188256788092)


Задание 5:

```
#!/bin/bash

file=$1

chmod 755 "./$file"

sudo cp "$file" /usr/local/bin/
```

<img width="881" alt="image" src="https://github.com/user-attachments/assets/37b8494b-2774-471c-9256-288f02117a5b">


