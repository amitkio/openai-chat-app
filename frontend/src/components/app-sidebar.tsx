import * as React from "react";
import { InboxIcon, Minus, Moon, Plus } from "lucide-react";

import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
} from "@/components/ui/sidebar";
import type { Chat } from "@/lib/utils";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "./ui/collapsible";
import { ChatList } from "@/components/chat-list";

import { createChat } from "@/lib/utils";

export function AppSidebar({
  chats,
  setChats,
  chatId,
  setChatId,
  ...props
}: React.ComponentProps<typeof Sidebar> & {
  chats?: Chat[];
  chatId: number | null;
  setChats: React.Dispatch<React.SetStateAction<Chat[] | undefined>>;
  setChatId: React.Dispatch<React.SetStateAction<number | null>>;
}) {
  const [hoverChat, setHoverChat] = React.useState<number>();

  return (
    <Sidebar {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg" asChild>
              <a href="#">
                <div className="bg-sidebar-primary text-sidebar-primary-foreground flex aspect-square size-8 items-center justify-center rounded-lg">
                  <Moon className="size-4 text-primary-foreground" />
                </div>
                <div className="flex flex-col gap-0.5 leading-none">
                  <span className="font-medium">chat-app</span>
                  <span className="">v1.0.0</span>
                </div>
              </a>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarMenu>
            <SidebarMenuButton
              tooltip="Quick Create"
              className="bg-primary text-primary-foreground justify-center hover:bg-primary-foreground hover:text-primary active:bg-primary/90 active:text-primary-foreground min-w-8 duration-200 ease-linear"
              onClick={() => {
                createChat(chats, setChats, setChatId);
              }}
            >
              <InboxIcon />
              <span>New Chat</span>
            </SidebarMenuButton>
            <Collapsible defaultOpen={true} className="group/collapsible">
              <SidebarMenuItem>
                <CollapsibleTrigger asChild>
                  <SidebarMenuButton>
                    Your Chats{" "}
                    <Plus className="ml-auto group-data-[state=open]/collapsible:hidden" />
                    <Minus className="ml-auto group-data-[state=closed]/collapsible:hidden" />
                  </SidebarMenuButton>
                </CollapsibleTrigger>
                <CollapsibleContent>
                  <ChatList
                    chats={chats}
                    chatId={chatId}
                    setChatId={setChatId}
                    setHoverChat={setHoverChat}
                    hoverChat={hoverChat}
                    setChats={setChats}
                  />
                </CollapsibleContent>
              </SidebarMenuItem>
            </Collapsible>
          </SidebarMenu>
        </SidebarGroup>
      </SidebarContent>
      <SidebarRail />
    </Sidebar>
  );
}
