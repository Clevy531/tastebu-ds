const About = () => {
  return (
    <section className="py-20 px-4 bg-secondary/30">
      <div className="container mx-auto max-w-4xl">
        <div className="text-center">
          <h2 className="text-4xl md:text-5xl font-bold mb-6 text-foreground">
            Our Story
          </h2>
          <div className="space-y-4 text-lg text-muted-foreground">
            <p>
              At Taste, we believe that food is more than sustenance—it's an experience, 
              a celebration, and a connection to the world around us.
            </p>
            <p>
              Our passion for culinary excellence drives us to source the finest ingredients, 
              work with local farmers, and create dishes that honor both tradition and innovation.
            </p>
            <p className="text-foreground font-medium">
              Every plate we serve is a testament to our commitment to quality, 
              creativity, and the joy of sharing exceptional food.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default About;
