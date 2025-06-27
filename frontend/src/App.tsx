import "./App.css";
import { ThemeProvider } from "./components/theme-provider";
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "./components/ui/sidebar";
import { AppSidebar } from "./components/app-sidebar";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbList,
  BreadcrumbPage,
} from "./components/ui/breadcrumb";
import { Separator } from "@radix-ui/react-separator";
import { CardsChat } from "./components/chat";
import { ModeToggle } from "./components/mode-toggle";
import { useEffect, useState } from "react";
import { type Chat } from "@/lib/utils";

function App() {
  const [chats, setChats] = useState<Chat[]>();
  const [chatId, setChatId] = useState<number | null>(null);
  useEffect(() => {
    const requestChats = async () => {
      const data = await fetch(
        `http://${
          import.meta.env.VITE_AZURE_FUNCTIONS_ENDPOINT
        }/api/fetch_chats`
      );
      const fetchedChats: Chat[] = await data.json();
      setChatId(fetchedChats[0].id);
      setChats(fetchedChats);
    };
    requestChats();
  }, []);
  return (
    <>
      <ThemeProvider defaultTheme="light" storageKey="vite-ui-theme">
        <SidebarProvider>
          <AppSidebar
            chats={chats}
            setChats={setChats}
            chatId={chatId}
            setChatId={setChatId}
          />
          <SidebarInset>
            <header className="flex h-16 shrink-0 items-center gap-2 border-b px-4">
              <SidebarTrigger className="-ml-1" />
              <Separator
                orientation="vertical"
                className="mr-2 data-[orientation=vertical]:h-4"
              />
              <Breadcrumb>
                <BreadcrumbList>
                  <BreadcrumbItem className="hidden md:block">
                    <BreadcrumbPage className="text-lg">
                      {chats?.find((chat) => chat.id === chatId)?.title}
                    </BreadcrumbPage>
                  </BreadcrumbItem>
                </BreadcrumbList>
              </Breadcrumb>
              <BreadcrumbItem className="ml-auto">
                <BreadcrumbPage>
                  <ModeToggle />
                </BreadcrumbPage>
              </BreadcrumbItem>
            </header>
            <div className="flex flex-1 flex-col gap-4 py-2 md:p-4 items-end">
              <CardsChat chatId={chatId || 0} />
            </div>
          </SidebarInset>
        </SidebarProvider>
      </ThemeProvider>
    </>
  );
}

export default App;
