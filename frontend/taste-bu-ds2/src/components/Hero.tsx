import { Button } from "@/components/ui/button";
import heroImage from "@/assets/hero-image.jpg";

const Hero = () => {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      <div
        className="absolute inset-0 bg-cover bg-center"
        style={{ backgroundImage: `url(${heroImage})` }}
      >
        <div className="absolute inset-0 bg-gradient-to-r from-background/95 via-background/80 to-background/60" />
      </div>
      
      <div className="relative z-10 container mx-auto px-4 py-20 text-center md:text-left">
        <div className="max-w-2xl mx-auto md:mx-0">
          <h1 className="text-5xl md:text-7xl font-bold mb-6 text-foreground animate-in fade-in slide-in-from-bottom-4 duration-1000">
            Taste the
            <span className="block text-primary">Extraordinary</span>
          </h1>
          <p className="text-lg md:text-xl mb-8 text-muted-foreground animate-in fade-in slide-in-from-bottom-4 duration-1000 delay-200">
            Experience culinary artistry where every dish tells a story. 
            Fresh ingredients, bold flavors, unforgettable moments.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center md:justify-start animate-in fade-in slide-in-from-bottom-4 duration-1000 delay-300">
            <Button variant="hero" size="lg">
              Reserve a Table
            </Button>
            <Button variant="outline" size="lg" className="border-2">
              View Menu
            </Button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;
