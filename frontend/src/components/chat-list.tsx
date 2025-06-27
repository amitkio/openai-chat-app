import { Trash } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  SidebarMenuSub,
  SidebarMenuSubButton,
  SidebarMenuSubItem,
} from "@/components/ui/sidebar";
import type { Chat } from "@/lib/utils";
import type React from "react";

interface ChatListProps {
  chats: Chat[] | undefined;
  setChatId: (id: number) => void;
  chatId: number | null;
  setHoverChat: React.Dispatch<React.SetStateAction<number | undefined>>;
  hoverChat: number | undefined;
  setChats: React.Dispatch<React.SetStateAction<Chat[] | undefined>>;
}

export function ChatList({
  chats,
  setChatId,
  chatId,
  setHoverChat,
  hoverChat,
  setChats,
}: ChatListProps) {
  const deleteChat = async (e: React.MouseEvent, chat_id: number) => {
    e.stopPropagation();
    await fetch(
      `http://${
        import.meta.env.VITE_AZURE_FUNCTIONS_ENDPOINT
      }/api/delete_chat/${chat_id}`,
      {
        method: "DELETE",
      }
    );
    if (chats) {
      const results = chats.filter((chat) => chat.id != chat_id);
      if (chatId === chat_id) {
        setChatId(results[0].id);
      }
      setChats([...results]);
    }
  };

  return (
    <SidebarMenuSub>
      {chats?.map((chat) => (
        <SidebarMenuSubItem key={chat?.id}>
          <SidebarMenuSubButton
            onClick={() => {
              setChatId(chat.id);
            }}
            asChild
            isActive={chatId === chat.id}
          >
            <div
              className="flex min-w-0 cursor-pointer whitespace-nowrap text-ellipsis overflow-hidden"
              onMouseOver={() => {
                setHoverChat(chat.id);
              }}
              onMouseOut={() => {
                setHoverChat(undefined);
              }}
            >
              <a className="w-full">
                {chat.title.length > 25
                  ? chat.title.slice(0, 25) + "..."
                  : chat.title}
              </a>
              <Button
                size="icon"
                variant="secondary"
                className={
                  chats?.length > 1 && hoverChat === chat.id
                    ? "inline-flex z-10 absolute right-0 top-1/2 -translate-y-1/2"
                    : "hidden"
                }
                onClick={(e) => {
                  deleteChat(e, chat.id);
                }}
              >
                <Trash color="#ff5569" />
              </Button>
            </div>
          </SidebarMenuSubButton>
        </SidebarMenuSubItem>
      ))}
    </SidebarMenuSub>
  );
}
