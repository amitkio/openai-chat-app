import { Input } from "@/components/ui/input"

export function InputFile() {
  return (
    <div className="grid w-full items-center gap-3">
      <Input id="files" type="file" />
    </div>
  )
}