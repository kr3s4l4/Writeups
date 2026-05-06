# Writeup: where_are_the_robots
**Categoría:** Easy
**Fecha de conversión:** 2026-04-24

---

riteup: Where are the robots?


Author: zaratec/Danny

Description: Can you find the robots?

URL: http://fickle-tempest.picoctf.net:60795

1. Initial Reconnaissance

Visiting the main page shows a simple HTML page with a message: "Where are the robots?".


Checking the source code (Ctrl+U) reveals nothing unusual—just a basic structure with no hidden content or comments.

2. Exploring robots.txt

The hint "robots" suggests checking the standard robots.txt file, which webmasters use to instruct web crawlers which parts of the site should not be accessed.


Navigating to http://fickle-tempest.picoctf.net:60795/robots.txt yields:

text


User-agent: *

Disallow: /cc6b1.html


This indicates that the file /cc6b1.html is disallowed for crawlers, but it is still accessible to humans.

3. Accessing the Disallowed File

Visiting http://fickle-tempest.picoctf.net:60795/cc6b1.html displays a page containing the **flag**:

html


<!doctype html>

<html>

```
  <head>
    <title>Where are the robots</title>
    ...
  </head>
  <body>
    <div class="container">
      <div class="content">
        <p>Guess you found the robots<br />
          <flag>picoCTF{******************}</flag></p>
      </div>
      ...
    </div>
  </body>
```

</html>



Summary: The challenge demonstrates how robots.txt can inadvertently expose hidden endpoints. By checking the standard robots.txt file and visiting the disallowed path, the flag is revealed.

