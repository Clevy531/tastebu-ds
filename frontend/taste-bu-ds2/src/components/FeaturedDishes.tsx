import { Card, CardContent } from "@/components/ui/card";
import dish1 from "@/assets/dish-1.jpg";
import dish2 from "@/assets/dish-2.jpg";
import dish3 from "@/assets/dish-3.jpg";

const dishes = [
  {
    name: "Handmade Pasta",
    description: "Fresh pasta with seasonal vegetables and aromatic herbs",
    image: dish1,
    price: "$24"
  },
  {
    name: "Grilled Salmon",
    description: "Wild-caught salmon with roasted vegetables and citrus",
    image: dish2,
    price: "$32"
  },
  {
    name: "Chocolate Decadence",
    description: "Rich chocolate dessert with fresh berries",
    image: dish3,
    price: "$14"
  }
];

const FeaturedDishes = () => {
  return (
    <section className="py-20 px-4">
      <div className="container mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-4 text-foreground">
            Featured Dishes
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Discover our chef's carefully crafted selections, made with the finest ingredients
          </p>
        </div>
        
        <div className="grid md:grid-cols-3 gap-8">
          {dishes.map((dish, index) => (
            <Card 
              key={index} 
              className="overflow-hidden hover:shadow-xl transition-all duration-300 hover:-translate-y-2 border-border/50"
            >
              <div className="aspect-square overflow-hidden">
                <img
                  src={dish.image}
                  alt={dish.name}
                  className="w-full h-full object-cover hover:scale-110 transition-transform duration-500"
                />
              </div>
              <CardContent className="p-6">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="text-2xl font-semibold text-foreground">
                    {dish.name}
                  </h3>
                  <span className="text-xl font-bold text-primary">
                    {dish.price}
                  </span>
                </div>
                <p className="text-muted-foreground">
                  {dish.description}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};

export default FeaturedDishes;
