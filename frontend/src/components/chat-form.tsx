import { ArrowUpIcon, Paperclip } from "lucide-react";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

interface ChatFormProps {
  inputLength: number;
  setMessages: React.Dispatch<
    React.SetStateAction<{ role: string; content: string }[]>
  >;
  messages: { role: string; content: string }[];
  input: string;
  setInput: React.Dispatch<React.SetStateAction<string>>;
  handleFileChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  selectedFile: File | null;
}

export function ChatForm({
  inputLength,
  setMessages,
  messages,
  input,
  setInput,
  handleFileChange,
  selectedFile,
}: ChatFormProps) {
  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        if (inputLength === 0) return;
        setMessages([
          ...messages,
          {
            role: "user",
            content: input,
          },
        ]);
        setInput("");
      }}
      className="relative w-full"
    >
      <Textarea
        id="message"
        placeholder="Type your message..."
        className="flex-1 pr-10 z-10 resize-none !h-24"
        autoComplete="off"
        value={input}
        onChange={(event) => setInput(event.target.value)}
      />
      <div className="absolute flex transition-all duration-200 left-2 bottom-3 hover:opacity-100 w-max ml-2 z-10 bg-secondary rounded-2xl border-1 opacity-40 p-2">
        <label
          htmlFor="file-upload"
          className="cursor-pointer text-sm text-gray-50"
        >
          <Paperclip />
        </label>
        <input
          id="file-upload"
          type="file"
          className="hidden"
          onChange={handleFileChange}
        />
        <div
          className={cn(
            "ml-3 align-middle block",
            selectedFile ? "block" : "hidden"
          )}
        >
          {selectedFile?.name}
        </div>
      </div>
      <Button
        type="submit"
        size="icon"
        className="absolute top-1/2 right-2 size-6 -translate-y-1/2 rounded-full"
        disabled={inputLength === 0}
      >
        <ArrowUpIcon className="size-3.5" />

        <span className="sr-only">Send</span>
      </Button>
    </form>
  );
}
