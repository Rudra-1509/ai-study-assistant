import bootstrap
import controller
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"


def main():
    option=input("1>txt 2>pdf 3>img: ")
    ip = input("Paste the text or file path: ")
    result = controller.run(ip,int(option))

    print("\n===== STUDY ASSISTANT OUTPUT =====\n")
    for topic_id, data in result.items():
        print(f"Topic {topic_id}")
        print(f"Difficulty: {data['difficulty']}")
        print(f"Keywords: {', '.join(data['keywords'])}")
        print("\nExplanation:\n")
        print(data['explanation'])
        print("\n" + "-" * 50 + "\n")

if __name__ == "__main__":
    main()
