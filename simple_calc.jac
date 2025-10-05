walker simple_calc {
    with entry {
        import random;

        print(" Simple Random Calculator (Jac Generator)...");
        print("--------------------------------------------------");

        ops = ["+", "-", "*", "/"];
        questions = [];

        for i in range(5) {
            n1 = random.randint(2, 20);
            n2 = random.randint(1, 10);
            op = random.choice(ops);
            q = str(n1) + " " + op + " " + str(n2);
            questions.append(q);
        }

        # Write to a text file
        file_path = "questions.txt";
        file = open(file_path, "w");
        for q in questions {
            file.write(q + "\n");
        }
        file.close();

        print("✅ Saved 5 random questions to questions.txt");
        print("Now run: python3 math_helper.py");
    }
}