"use client";

import Image from "next/image";
import { Button } from "../../ui/button";
import { Note, User, Tag } from "@prisma/client";

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTrigger,
} from "@/components/ui/dialog";
import SpecializedYoutubeIntegration from "./youtube";
import SpecializedPdfIntegration from "./pdf";

interface SpecializedAIProps {
  note: Note & {
    user: User;
    tags: Tag[];
  };
  settingsOff?: boolean;
}

const SpecializedAI: React.FC<SpecializedAIProps> = ({ note }) => {
  return (
    <div className="fixed bottom-0 ml-8 mb-8 z-50">
      <Dialog>
        <DialogTrigger asChild>
          <Button className="bg-aiButtonGradient hover:opacity-50 animate-spin relative border-4 z-50 border-cyan-400 rounded-full w-16 h-16">
            <Image
              src="/assets/images/abstract.png"
              alt="Generative AI"
              width={64}
              height={64}
              className="absolute"
            />
          </Button>
        </DialogTrigger>
        <DialogContent className="sm:max-w-[425px] md:max-w-[820px] p-0 border-2 border-secondary bg-foreground flex">
          <DialogHeader className="h-[425px] bg-aiButtonGradient w-[320px] relative flex justify-end items-end rounded-sm p-4">
            <h3 className="text-white font-extrabold uppercase text-6xl text-left">
              Special AI Mod
            </h3>

            <p className="text-white/30 font-medium">
              Make your notes even more powerful using specialized AI
              integrations.
            </p>
          </DialogHeader>
          <div className="py-4 pl-4 pr-12 grid grid-cols-2 gap-4">
            <SpecializedYoutubeIntegration note={note} />

            <SpecializedPdfIntegration note={note} />

            <Button className="h-fit bg-foreground w-auto flex flex-col items-start p-4 border border-secondary">
              <Image
                src="/assets/images/logos/image.webp"
                alt=""
                width={64}
                height={64}
                sizes="100vw"
              />

              <p className="font-medium text-white text-sm text-wrap text-left">
                Image Explainer
              </p>
              <span className="text-wrap text-white/30 text-xs text-left">
                Upload an image and the specialised AI will summarise it for
                you.
              </span>
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default SpecializedAI;
