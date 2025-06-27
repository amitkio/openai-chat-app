"use client";

import * as React from "react";
import { useEffect } from "react";
import { cn } from "@/lib/utils";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
} from "@/components/ui/card";

import ReactMarkdown from "react-markdown";
import { useSidebar } from "@/components/ui/sidebar";
import { customMarkdownComponents } from "@/components/custom-markdown-components";
import gptAvatar from "@/assets/avatars/01.webp";
import { Skeleton } from "@/components/ui/skeleton";
import { toast, Toaster } from "sonner";
import { FileList } from "@/components/file-list";
import { ChatForm } from "@/components/chat-form";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Terminal } from "lucide-react";

interface ChatResponse {
  messages: Array<{
    role: string;
    value: string;
  }>;
  files: Array<string>;
}

interface ErrorState {
  hasError: boolean;
  message: string;
}

export function CardsChat({ chatId }: { chatId: number }) {
  const [messages, setMessages] = React.useState([
    {
      role: "agent",
      content: "Hi, how may I help you?",
    },
  ]);

  const [input, setInput] = React.useState("");
  const [skeletonState, setSkeletonState] = React.useState<boolean>(false);
  const [selectedFile, setSelectedFile] = React.useState<File | null>(null);
  const [files, setFiles] = React.useState<Array<string>>([]);
  const [appError, setAppError] = React.useState<ErrorState>({
    hasError: false,
    message: "",
  });

  const inputLength = input.trim().length;
  const { open: SidebarOpen } = useSidebar();

  const firstRender = React.useRef<number>(messages.length);
  const agentMessage = React.useRef<string>("");
  const messagesEndRef = React.useRef<null | HTMLDivElement>(null);

  const clearError = () => {
    setAppError({ hasError: false, message: "" });
  };

  useEffect(() => {
    setTimeout(clearError, 10000);
  }, [appError]);

  useEffect(() => {
    const fetchChat = async () => {
      setSkeletonState(true);
      setMessages([]);

      try {
        const response = await fetch(
          `http://${
            import.meta.env.VITE_AZURE_FUNCTIONS_ENDPOINT
          }/api/fetch_chat?chat_id=${chatId}`
        );

        if (!response.ok) {
          const errorDetail = await response.text();
          throw new Error(
            `Failed to fetch chat: ${response.status} ${errorDetail}`
          );
        }

        let data: ChatResponse = await response.json();
        setFiles(data.files);

        let fetchedMessages = data.messages.map(({ role, value }) => {
          return { role: role.toLowerCase(), content: value };
        });
        firstRender.current = fetchedMessages.length;
        setMessages(fetchedMessages);
      } catch (error: any) {
        console.error("Error fetching chat:", error);
        setAppError({
          hasError: true,
          message: `Failed to load chat history: ${
            error.message || "Unknown error"
          }`,
        });
      } finally {
        setSkeletonState(false);
      }
    };
    fetchChat();
  }, [chatId]);

  useEffect(() => {
    if (firstRender.current === messages.length) {
      return;
    }

    const lastMessage = messages[messages.length - 1];
    if (!lastMessage || lastMessage.role !== "user") {
      return;
    }

    setSkeletonState(true);

    if (chatId === -1) {
    }

    const gptResponse = async () => {
      if (selectedFile) {
        const uploadSuccess = await handleUpload();
        if (!uploadSuccess) {
          setSkeletonState(false);
          return;
        }
      }

      const data = JSON.stringify({
        chatId: chatId,
        q: messages[messages.length - 1].content,
      });

      messagesEndRef.current?.scrollIntoView({
        behavior: "smooth",
        block: "end",
      });

      try {
        const response = await fetch(
          `http://${
            import.meta.env.VITE_AZURE_FUNCTIONS_ENDPOINT
          }/api/request_gpt`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: data,
          }
        );

        if (!response.ok) {
          const errorText = await response.text();
          const errorMessage = errorText.startsWith("data: ERROR:")
            ? errorText.replace("data: ERROR:", "").trim()
            : `API error: ${response.status} ${response.statusText}`;
          throw new Error(errorMessage);
        }

        setSkeletonState(false);
        agentMessage.current = "";

        const reader = response.body?.getReader();
        const textDecoder = new TextDecoder();

        if (!reader) {
          throw new Error("Failed to get response reader for streaming.");
        }

        while (true) {
          const { done, value } = await reader.read();
          if (done) {
            agentMessage.current = "";
            break;
          }

          const decodedValue = textDecoder.decode(value, { stream: true });
          agentMessage.current += decodedValue;

          if (!appError.hasError) {
            if (messages[messages.length - 1].role === "user") {
              firstRender.current = messages.length + 1;
              setMessages([
                ...messages,
                {
                  role: "agent",
                  content: agentMessage.current,
                },
              ]);
            } else {
              setMessages([
                ...messages.slice(0, -1),
                {
                  role: "agent",
                  content: agentMessage.current,
                },
              ]);
            }
          }
          messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
        }
      } catch (error: any) {
        console.error("Error generating GPT response:", error);
        setAppError({
          hasError: true,
          message: `Error during AI response: ${
            error.message || "Unknown error"
          }`,
        });
        setSkeletonState(false);
      }
    };
    gptResponse();
  }, [messages]);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (!event.target.files) return;
    const file = event.target.files[0];
    if (
      [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      ].includes(file.type.toLowerCase())
    )
      setSelectedFile(file);
    else {
      toast.error("That file type is not supported!");
      setSelectedFile(null);
    }
    return;
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setAppError({ hasError: true, message: "No file selected for upload." });
      return false;
    }
    const formData = new FormData();

    formData.append("chatId", chatId.toString());

    formData.append("file", selectedFile);

    try {
      const response = await fetch(
        `http://${import.meta.env.VITE_AZURE_FUNCTIONS_ENDPOINT}/api/upload`,
        {
          method: "POST",
          body: formData,
        }
      );

      if (response.ok) {
        toast.success(`File uploaded successfully`, {
          description: `${selectedFile.name} - ${
            selectedFile.size / (1024 * 1024)
          } MB`,
        });
        setFiles([...files, selectedFile.name]);
        setSelectedFile(null);
        return true;
      } else {
        const errorData: { message?: string } = await response
          .json()
          .catch(() => ({ message: response.statusText }));
        console.error("Upload error:", errorData);
        setAppError({
          hasError: true,
          message: `File upload failed: ${
            errorData.message || response.statusText
          }`,
        });
        return false;
      }
    } catch (error: any) {
      console.error("Network or unexpected error during upload:", error);
      setAppError({
        hasError: true,
        message: `Network error during upload: ${
          error.message || "Please check your connection."
        }`,
      });
      return false;
    }
  };

  return (
    <>
      <Card
        className={cn(
          "md:h-[calc(100vh-6rem)] h-[calc(100vh-5rem)] overflow-auto  transition-[width] w-[100vw] duration-200 ease-linear",
          SidebarOpen
            ? "md:w-[calc(100vw-var(--sidebar-width)-2em)]"
            : "md:w-full md:ml-0"
        )}
      >
        <CardHeader className="flex flex-row items-center justify-between">
          <div className="flex items-center gap-4">
            <Avatar className="border">
              <AvatarImage src={gptAvatar} alt="Image" />

              <AvatarFallback>S</AvatarFallback>
            </Avatar>

            <div className="flex flex-col gap-0.5">
              <p className="text-sm leading-none font-medium">GPT 4.0 Turbo</p>

              <p className="text-muted-foreground text-xs">Oct 2023 Cutoff</p>
            </div>
          </div>
          <FileList files={files} />
        </CardHeader>

        <CardContent className="flex-1 overflow-y-auto">
          {appError.hasError && (
            <Alert variant="destructive" className="mb-4">
              <Terminal className="h-4 w-4" />
              <AlertTitle>Error!</AlertTitle>
              <AlertDescription>{appError.message}</AlertDescription>
            </Alert>
          )}

          <div className="flex flex-col gap-4">
            {messages.map((message, index) => (
              <div
                key={index}
                className={cn(
                  "flex max-w-[75%] w-max wrap-break-word flex-col gap-2 rounded-lg px-3 py-2 text-sm whitespace-normal",
                  message.role === "user"
                    ? "bg-primary text-primary-foreground ml-auto"
                    : "bg-muted"
                )}
              >
                <ReactMarkdown components={customMarkdownComponents}>
                  {message.content}
                </ReactMarkdown>
              </div>
            ))}
          </div>
          <Skeleton
            className={cn(
              "none w-36 h-8 mt-4 wrap-break-word flex-col gap-2 rounded-lg px-3 py-2 text-sm whitespace-pre-wrap",
              skeletonState ? "block" : "hidden"
            )}
          ></Skeleton>
          <div ref={messagesEndRef} />
        </CardContent>

        <CardFooter className="">
          <ChatForm
            inputLength={inputLength}
            messages={messages}
            setMessages={setMessages}
            handleFileChange={handleFileChange}
            input={input}
            selectedFile={selectedFile}
            setInput={setInput}
          />
          <Toaster />
        </CardFooter>
      </Card>
    </>
  );
}
