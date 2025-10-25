import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { MapPin, Phone, Clock } from "lucide-react";

const Contact = () => {
  return (
    <section className="py-20 px-4">
      <div className="container mx-auto max-w-6xl">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-4 text-foreground">
            Visit Us
          </h2>
          <p className="text-lg text-muted-foreground">
            We'd love to welcome you to Taste
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 mb-12">
          <Card className="border-border/50">
            <CardContent className="p-6 text-center">
              <MapPin className="w-8 h-8 mx-auto mb-4 text-primary" />
              <h3 className="text-xl font-semibold mb-2 text-foreground">Location</h3>
              <p className="text-muted-foreground">
                123 Culinary Street<br />
                Downtown District<br />
                New York, NY 10001
              </p>
            </CardContent>
          </Card>

          <Card className="border-border/50">
            <CardContent className="p-6 text-center">
              <Phone className="w-8 h-8 mx-auto mb-4 text-primary" />
              <h3 className="text-xl font-semibold mb-2 text-foreground">Contact</h3>
              <p className="text-muted-foreground">
                (555) 123-4567<br />
                hello@taste.restaurant<br />
                @taste
              </p>
            </CardContent>
          </Card>

          <Card className="border-border/50">
            <CardContent className="p-6 text-center">
              <Clock className="w-8 h-8 mx-auto mb-4 text-primary" />
              <h3 className="text-xl font-semibold mb-2 text-foreground">Hours</h3>
              <p className="text-muted-foreground">
                Mon-Thu: 5PM - 10PM<br />
                Fri-Sat: 5PM - 11PM<br />
                Sunday: Closed
              </p>
            </CardContent>
          </Card>
        </div>

        <div className="text-center">
          <Button variant="hero" size="lg">
            Make a Reservation
          </Button>
        </div>
      </div>
    </section>
  );
};

export default Contact;
