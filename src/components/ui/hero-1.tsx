import React from "react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { RocketIcon, ArrowRightIcon } from "lucide-react";

export function HeroSection() {
    return (
        <section className="mx-auto w-full max-w-5xl">
            {/* Top Shades */}
            <div
                aria-hidden="true"
                className="absolute inset-0 isolate hidden overflow-hidden contain-strict lg:block"
            >
                <div className="absolute inset-0 -top-14 isolate -z-10 bg-[radial-gradient(35%_80%_at_49%_0%,--theme(--color-foreground/.08),transparent)] contain-strict" />
            </div>

            {/* X Bold Faded Borders */}
            <div
                aria-hidden="true"
                className="absolute inset-0 mx-auto hidden min-h-screen w-full max-w-5xl lg:block"
            >
                <div className="mask-y-from-80 mask-y-to-100 absolute inset-y-0 left-0 z-10 h-full w-px bg-foreground/15" />
                <div className="mask-y-from-80 mask-y-to-100 absolute inset-y-0 right-0 z-10 h-full w-px bg-foreground/15" />
            </div>

            {/* main content */}

            <div className="relative flex flex-col items-center justify-center gap-5 pt-32 pb-30">
                {/* X Content Faded Borders */}
                <div
                    aria-hidden="true"
                    className="absolute inset-0 -z-1 size-full overflow-hidden"
                >
                    <div className="absolute inset-y-0 left-4 w-px bg-linear-to-b from-transparent via-border to-border md:left-8" />
                    <div className="absolute inset-y-0 right-4 w-px bg-linear-to-b from-transparent via-border to-border md:right-8" />
                    <div className="absolute inset-y-0 left-8 w-px bg-linear-to-b from-transparent via-border/50 to-border/50 md:left-12" />
                    <div className="absolute inset-y-0 right-8 w-px bg-linear-to-b from-transparent via-border/50 to-border/50 md:right-12" />
                </div>

                <a
                    className={cn(
                        "group mx-auto flex w-fit items-center gap-3 rounded-full border bg-card px-3 py-1 shadow",
                        "fade-in slide-in-from-bottom-10 animate-in fill-mode-backwards transition-all delay-500 duration-500 ease-out"
                    )}
                    href="#"
                >
                    <RocketIcon className="size-3 text-muted-foreground" />
                    <span className="text-xs">Veille IA 100% automatisée</span>
                    <span className="block h-5 border-l" />

                    <ArrowRightIcon className="size-3 duration-150 ease-out group-hover:translate-x-1" />
                </a>

                <h1
                    className={cn(
                        "fade-in slide-in-from-bottom-10 animate-in text-balance fill-mode-backwards text-center text-4xl tracking-tight delay-100 duration-500 ease-out md:text-5xl lg:text-6xl",
                        "text-shadow-premium"
                    )}
                >
                    Pulse.AI : Votre Boussole <br /> dans l&apos;Océan de l&apos;IA
                </h1>

                <p className="fade-in slide-in-from-bottom-10 mx-auto max-w-lg animate-in fill-mode-backwards text-center text-base text-foreground/80 tracking-wider delay-200 duration-500 ease-out sm:text-lg md:text-xl">
                    Extraction quotidienne des meilleures pépites : <br /> Substack, Beehiiv, et actualités actionnables.
                </p>

                <div className="fade-in slide-in-from-bottom-10 flex animate-in flex-row flex-wrap items-center justify-center gap-3 fill-mode-backwards pt-2 delay-300 duration-500 ease-out">
                    <Button className="rounded-full" size="lg" variant="secondary" onClick={() => document.getElementById('articles-grid')?.scrollIntoView({ behavior: 'smooth' })}>
                        Explorer le flux
                    </Button>
                    <Button className="rounded-full" size="lg" onClick={() => window.location.reload()}>
                        Sync Maintenant
                        <ArrowRightIcon
                            className="size-4 ms-2" data-icon="inline-end" />
                    </Button>
                </div>
            </div>
        </section>
    );
}

export function SourcesSection() {
    return (
        <section className="relative space-y-4 border-t pt-6 pb-10">
            <h2 className="text-center font-medium text-lg text-muted-foreground tracking-tight md:text-xl">
                Sources <span className="text-foreground">surveillées en continu</span>
            </h2>
            <div className="relative z-10 mx-auto max-w-4xl overflow-hidden py-4 [mask-image:linear-gradient(to_right,transparent,black,transparent)]">
                <div className="flex animate-marquee gap-12 whitespace-nowrap text-xl font-semibold text-muted-foreground/60">
                    {[1, 2].map((i) => (
                        <React.Fragment key={i}>
                            <span>Génération IA</span>
                            <span>Non Artificiel</span>
                            <span>Yassine Chabli</span>
                            <span>Préambule</span>
                            <span>Explorations IA</span>
                            <span>Upmynt</span>
                            <span>Mister IA</span>
                            <span>Vision IA</span>
                            <span>La Newsletter IA</span>
                        </React.Fragment>
                    ))}
                </div>
            </div>
        </section>
    );
}
