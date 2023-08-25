import os


def create(dest, source):
    current_data_dir = os.path.join(os.getcwd(), "sources", "test_data", source)
    print(current_data_dir)
    try:
        data_file = open(dest, "w")
        for entry in os.scandir(current_data_dir):
            if entry.is_file():
                print(entry)
                source_data_file = open(entry.path)
                data = source_data_file.read()
                data_file.write(data)
        data_file.close()

    except Exception as e:
        print(e)

def main():
    create("test.ld", "5")
    create("test1.ld", "dente")
    create("test2.ld", "dente_ok")


if __name__ == "__main__":
    main()