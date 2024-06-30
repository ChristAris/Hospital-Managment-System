# Χρησιμοποιούμε μια επίσημη Python εικόνα ως βάση
FROM python:3.11

# Ορίζουμε τον τρέχοντα κατάλογο εργασίας
WORKDIR /app

# Αντιγράφουμε τα requirements στο container
COPY requirements.txt requirements.txt

# Εγκαθιστούμε τις εξαρτήσεις από το requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Αντιγράφουμε το υπόλοιπο project στο container
COPY . .

# Εκθέτουμε την πόρτα 8080
EXPOSE 8080

# Ορίζουμε την εντολή εκκίνησης
CMD ["python", "app.py"]
