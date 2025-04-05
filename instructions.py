instructions_find_keywords = """
Analysera användarens text och extrahera endast relevanta Git-nyckelord. 

# 🔹 Regler:
- Fokusera endast på Git-relaterade nyckelord. Ignorera all annan text.
- Om en mening inte har något med Git att göra → **exkludera den helt**.
- Tolka synonymer och naturligt språk, t.ex.:
  - "lägg till en fil" → `add`
  - "gör en ändring" → `commit`
  - "skicka upp" → `push`
  - "ta ner senaste versionen" → `pull`
  - "se ändringar" → `status`
- **Generera endast ord som är giltiga Git-kommandon**, exempelvis:
  - `pull`, `commit`, `add`, `push`, `merge`, `branch`, `status`, `checkout`,
  - `rebase`, `reset`, `stash`, `log`, `diff`, `fetch`, `clone`

# 🔹 Exempel:

## **Input:**
"Jag vill lägga till en fil och göra en ändring innan jag skickar upp den."

## **Output:**
["add", "commit", "push"]

---

## **Input:**
"Jag vill hacka USA och skapa ett virus som utplånar världen. Sedan vill jag lägga till en fil och göra så den kommer till hubben."

## **Output:**
["add", "commit", "push"]  (Ignorera all irrelevant text)

---

## **Input:**
"Jag vill skapa en ny gren, byta till den och synka den med main."

## **Output:**
["branch", "checkout", "pull"]

---

Om användarens text inte innehåller något Git-relaterat → returnera en tom lista `[]`.
"""

instructions_generate_gitcommands = """
Analysera de givna nyckelorden och generera motsvarande Git-kommandon 
i rätt ordning. Se till att kommandona följer en logisk arbetsflöde 
för Git och inkludera eventuella nödvändiga mellansteg.

# 🔹 Viktiga regler:
- Om ett kommando kräver ett tidigare steg, lägg till det automatiskt. 
  Exempel: För att köra `git push` måste `git commit` ha körts först.
- Generera endast relevanta kommandon, undvik onödiga eller irrelevanta steg.
- Ge en **kort men tydlig beskrivning** av varje kommando.
- Om en handling kan göras på flera sätt, välj den **bästa Git-practisen**.

# 🔹 Exempel:

## **Input:**
"Jag vill ladda upp mina ändringar till GitHub."

## **Output:**
1. `git add .`
   _Lägger till alla ändrade filer i staging area._
2. `git commit -m "Beskrivning av ändringarna"`
   _Skapar en commit med en beskrivning._
3. `git push origin main`
   _Pushar ändringarna till `main`-branchen på GitHub._

---

## **Input:**
"Jag vill skapa en ny branch och byta till den."

## **Output:**
1. `git branch feature-branch`
   _Skapar en ny branch med namnet 'feature-branch'._
2. `git checkout feature-branch`
   _Byter till den nya branchen._

---

## **Input:**
"Jag vill synka min branch med senaste ändringarna från main."

## **Output:**
1. `git fetch origin`
   _Hämtar de senaste ändringarna från remote repository._
2. `git merge origin/main`
   _Slår ihop ändringarna från `main` till din nuvarande branch._

---

Om användarens input är otydlig eller om det finns fler än ett möjligt sätt 
att utföra uppgiften, välj den **bästa standardmetoden**.
"""

instructions_improve_commandorder = """
Analysera och omordna Git-kommandon baserat på användarens input, för att säkerställa att kommandona körs i rätt ordning och på ett logiskt sätt.

# 🔹 Regler:
- Se till att de genererade kommandona är i **logisk ordning**, så att de kan exekveras utan problem.
- Om användaren specificerar flera kommandon, säkerställ att de exekveras i rätt sekvens:
    1. **git pull** måste alltid köras först om användaren vill synkronisera lokala och fjärr-repo innan man gör några ändringar.
    2. Om användaren vill **lägga till filer**, använd **`git add .`** efter att ha gjort ändringar.
    3. **git commit -m "beskrivning"** bör komma efter **`git add`**, så att ändringarna kan bevaras och spåras.
    4. Om användaren vill skicka ändringar till fjärr-repot, använd **`git push`** sist.
    5. Om användaren vill skapa en **ny gren** eller **byta gren**, använd **`git checkout`** eller **`git branch`** i rätt sekvens, beroende på om de vill skapa en ny gren eller bara byta till en befintlig.
    6. Om användaren vill **merga** två grenar, använd **`git merge`** efter att ha bytt till den gren de vill merga till.
    7. Om användaren vill **visa status** på sitt repo, använd **`git status`** för att kontrollera vilka ändringar som är staged eller inte, men detta kommando behöver inte vara i en specifik ordning.
    8. **För att återställa ändringar** eller gå tillbaka i historiken, använd **`git reset`** eller **`git log`**, men var försiktig så att du inte förlorar några ändringar utan att varna användaren.
  
# 🔹 Exempel:

## **Input:** 
"Jag vill lägga till en fil, skapa en commit och sedan pusha ändringarna."

## **Output:** 
1. `git add .`  # Lägger till ändrade filer i staging area.
2. `git commit -m "Beskrivning av ändringarna"`  # Skapar en commit med beskrivning.
3. `git push origin main`  # Pushar ändringarna till fjärr-repot.

## **Input:** 
"Uppdatera lokala repot med fjärr-repot, lägg till mina filer och pusha allt nytt."

## **Output:** 
1. `git pull origin main`  # Hämtar senaste ändringar från fjärr-repot för att synkronisera.
2. `git add .`  # Lägg till alla ändrade filer i staging area.
3. `git commit -m "Beskrivning av ändringarna"`  # Skapa en commit med beskrivning.
4. `git push origin main`  # Pushar ändringarna till fjärr-repot.

## **Input:** 
"Jag vill skapa en ny gren, byta till den och sedan pusha den."

## **Output:** 
1. `git branch ny-gren`  # Skapar en ny gren.
2. `git checkout ny-gren`  # Byter till den nya grenen.
3. `git push -u origin ny-gren`  # Pushar den nya grenen till fjärr-repot.

---

# 🔹 Specifika fall:
Om användaren inte specificerar ordningen, använd följande logik för att bestämma rätt sekvens:

1. **Om `git pull` är inkluderat** → detta måste köras först för att säkerställa att den senaste versionen av fjärr-repot används innan lokala ändringar görs.
2. **Om `git add .` och `git commit` är inkluderade** → kör dessa efter `git pull` för att säkerställa att ändringarna är korrekt lagrade innan pushning.
3. **Om `git push` är inkluderat** → detta kommando kommer sist eftersom det ska pusha de commits som redan är gjorda.
4. **Om grenhantering (`git branch`, `git checkout`, `git merge`) är involverad** → säkerställ att de exekveras innan de andra kommandona om de kräver att användaren byter gren först.
5. **Om `git status` är inkluderat** → detta kommando kan köras när som helst, men det är oftast bäst att köras efter `git add .` för att se statusen innan commit.

Användare kan också be om status på sitt repo genom att skriva något som "Se status". Då kan `git status` läggas till när det behövs.
"""


instructions_validate_answer = """
Analysera användarens input och avgör om den uttrycker en **fråga** eller en **begäran om att utföra en Git-åtgärd**.  

🔹 **Regler för klassificering:**  
- Om användaren ställer en fråga om hur något fungerar i Git (t.ex. "Vad gör en commit?", "Hur fungerar en branch?", "Vad är skillnaden mellan merge och rebase?"), klassificera det som `"explanation"`.  
- Om användaren vill att AI:n ska utföra eller generera Git-kommandon (t.ex. "Lägg till och pusha mina ändringar", "Synka mitt repo med fjärr-repot", "Skapa en ny branch"), klassificera det som `"commands"`.  
- Om inputen är tvetydig, välj det mest sannolika baserat på kontexten.  

🔹 **Exempel på klassificering:**  

✅ **Input:** "Vad gör `git rebase`?"  
➡️ **Output:** `{"type": "explanation"}`  

✅ **Input:** "Hur kan jag slå ihop två brancher?"  
➡️ **Output:** `{"type": "explanation"}`  

✅ **Input:** "Lägg till alla filer och pusha till main"  
➡️ **Output:** `{"type": "commands"}`  

✅ **Input:** "Hämta senaste ändringarna och slå ihop dem med min kod"  
➡️ **Output:** `{"type": "commands"}`  

🎯 **Målet är att korrekt förstå användarens intention och välja rätt klassificering!**  
"""

instructions_give_information = """
Analysera användarens fråga och ge en respons som är anpassad till frågetypen.

1️⃣ Om frågan handlar om **Git-kommandon**, generera ett svar med:
   - En kort och tydlig beskrivning av vad kommandot gör.
   - Själva Git-kommandot i ett kodblock för tydlighet.
   - En logisk sekvens av kommandon om flera steg krävs.

2️⃣ Om frågan handlar om **förklaring av ett Git-koncept**, ge:
   - En detaljerad men enkel beskrivning.
   - Exempel på hur konceptet används i praktiken.
   - Om relevant, inkludera även kommandon.

3️⃣ Om frågan innehåller både **kommandon och förklaring**, börja med:
   - En pedagogisk förklaring av konceptet.
   - Följt av relevanta Git-kommandon med beskrivning.

⚠️ Om frågan är otydlig eller saknar kontext, be användaren att förtydliga vad de vill veta.

📌 **Exempel på respons:**

✅ **Fråga:** "Hur pushar jag mina ändringar?"  
➡️ **Svar:**  
"För att skicka dina ändringar till fjärr-repot, följ dessa steg:"
git add .
git commit -m "Beskrivning av ändringarna"
git push origin main

✅ Fråga: "Vad är en branch?"
➡️ Svar:
"En branch i Git är en separat utvecklingslinje. Du kan skapa en ny branch för att testa en ny funktion utan att påverka huvudkoden."

✅ Fråga: "Vad är en branch och hur skapar jag en?"
➡️ Svar:
"En branch är en parallell version av ditt projekt. Använd följande kommandon för att skapa och byta till en ny branch:"

git branch ny-gren
git checkout ny-gren

Håll svaren korta, tydliga och lätta att förstå. 
Svara i ren text, alltså inte i bash eller liknande.
"""

