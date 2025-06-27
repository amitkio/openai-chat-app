import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export interface Chat {
  id: number,
  title: string
}

export const createChat = async (chats: Chat[] | undefined, setChats: React.Dispatch<React.SetStateAction<Chat[] | undefined>>, setChatId: React.Dispatch<React.SetStateAction<number | null>>) => {
    const response = await fetch(`http://${import.meta.env.VITE_AZURE_FUNCTIONS_ENDPOINT}/api/create_chat`, {
      method: "POST",
    });
    const chat: Chat = await response.json();
    if (chats) {
      setChats([...chats, chat]);
    } else {
      setChats([chat]);
    }
    setChatId(chat.id);
  };