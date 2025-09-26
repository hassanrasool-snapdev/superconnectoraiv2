'use client';

import { useEffect, useState } from 'react';
import { Heart } from 'lucide-react';

interface Quote {
  text: string;
  author: string;
}

const inspirationalQuotes: Quote[] = [
  // Updated first quote - fresh inspiration
  {
    text: "The best way to make a difference in the world is to start by making a difference in your own community.",
    author: "Unknown"
  },
  {
    text: "A single act of kindness throws out roots in all directions, and the roots spring up and make new trees.",
    author: "Amelia Earhart"
  },
  {
    text: "If you can't feed a hundred people, then feed just one.",
    author: "Mother Teresa"
  },
  {
    text: "To the world you may be one person, but to one person you may be the world.",
    author: "Dr. Seuss"
  },
  // Additional 48+ quotes to ensure a full year of unique weekly quotes
  {
    text: "The best way to find yourself is to lose yourself in the service of others.",
    author: "Mahatma Gandhi"
  },
  {
    text: "We make a living by what we get, but we make a life by what we give.",
    author: "Winston Churchill"
  },
  {
    text: "The meaning of life is to find your gift. The purpose of life is to give it away.",
    author: "Pablo Picasso"
  },
  {
    text: "Kindness is a language which the deaf can hear and the blind can see.",
    author: "Mark Twain"
  },
  {
    text: "How wonderful it is that nobody need wait a single moment before starting to improve the world.",
    author: "Anne Frank"
  },
  {
    text: "The smallest act of kindness is worth more than the grandest intention.",
    author: "Oscar Wilde"
  },
  {
    text: "We rise by lifting others.",
    author: "Robert Ingersoll"
  },
  {
    text: "What we do for ourselves dies with us. What we do for others and the world remains and is immortal.",
    author: "Albert Pike"
  },
  {
    text: "Be the change you wish to see in the world.",
    author: "Mahatma Gandhi"
  },
  {
    text: "The purpose of human life is to serve, and to show compassion and the will to help others.",
    author: "Albert Schweitzer"
  },
  {
    text: "Remember that the happiest people are not those getting more, but those giving more.",
    author: "H. Jackson Brown Jr."
  },
  {
    text: "Service to others is the rent you pay for your room here on earth.",
    author: "Muhammad Ali"
  },
  {
    text: "The best way to cheer yourself up is to try to cheer somebody else up.",
    author: "Mark Twain"
  },
  {
    text: "No act of kindness, no matter how small, is ever wasted.",
    author: "Aesop"
  },
  {
    text: "Alone we can do so little; together we can do so much.",
    author: "Helen Keller"
  },
  {
    text: "The good you do today may be forgotten tomorrow. Do good anyway.",
    author: "Mother Teresa"
  },
  {
    text: "Carry out a random act of kindness, with no expectation of reward, safe in the knowledge that one day someone might do the same for you.",
    author: "Princess Diana"
  },
  {
    text: "Too often we underestimate the power of a touch, a smile, a kind word, a listening ear, an honest compliment, or the smallest act of caring.",
    author: "Leo Buscaglia"
  },
  {
    text: "The fragrance always stays in the hand that gives the rose.",
    author: "George William Curtis"
  },
  {
    text: "Giving is not just about making a donation. It is about making a difference.",
    author: "Kathy Calvin"
  },
  {
    text: "We cannot live only for ourselves. A thousand fibers connect us with our fellow men.",
    author: "Herman Melville"
  },
  {
    text: "The value of a man resides in what he gives and not in what he is capable of receiving.",
    author: "Albert Einstein"
  },
  {
    text: "You have not lived today until you have done something for someone who can never repay you.",
    author: "John Bunyan"
  },
  {
    text: "Every small act of kindness creates ripples that can change the world in ways we may never see.",
    author: "Rachel Joy Scott"
  },
  {
    text: "It's not how much we give but how much love we put into giving.",
    author: "Mother Teresa"
  },
  {
    text: "The only ones among you who will be really happy are those who will have sought and found how to serve.",
    author: "Albert Schweitzer"
  },
  {
    text: "Generosity is giving more than you can, and pride is taking less than you need.",
    author: "Khalil Gibran"
  },
  {
    text: "The heart that gives, gathers.",
    author: "Tao Te Ching"
  },
  {
    text: "We make our living by what we get, but we make our life by what we give.",
    author: "Norman MacEwan"
  },
  {
    text: "A kind gesture can reach a wound that only compassion can heal.",
    author: "Steve Maraboli"
  },
  {
    text: "The wise find pleasure in water; the virtuous find pleasure in hills. The wise are active; the virtuous are tranquil. The wise are joyful; the virtuous are long-lived.",
    author: "Confucius"
  },
  {
    text: "Love and compassion are necessities, not luxuries. Without them, humanity cannot survive.",
    author: "Dalai Lama"
  },
  {
    text: "The greatest gift you can give someone is your time, your attention, your love, your concern.",
    author: "Joel Osteen"
  },
  {
    text: "Compassion is not a relationship between the healer and the wounded. It's a relationship between equals.",
    author: "Pema Chödrön"
  },
  {
    text: "The simplest acts of kindness are by far more powerful than a thousand heads bowing in prayer.",
    author: "Mahatma Gandhi"
  },
  {
    text: "Wherever there is a human being, there is an opportunity for a kindness.",
    author: "Lucius Annaeus Seneca"
  },
  {
    text: "Real generosity is doing something nice for someone who will never find out.",
    author: "Frank A. Clark"
  },
  {
    text: "The currency of real networking is not greed but generosity.",
    author: "Keith Ferrazzi"
  },
  {
    text: "We are here to add what we can to life, not to get what we can from life.",
    author: "William Osler"
  },
  {
    text: "The life of a man consists not in seeing visions and in dreaming dreams, but in active charity and in willing service.",
    author: "Henry Wadsworth Longfellow"
  },
  {
    text: "Kindness in words creates confidence. Kindness in thinking creates profoundness. Kindness in giving creates love.",
    author: "Lao Tzu"
  },
  {
    text: "In a world where you can be anything, be kind. Your kindness might be the light someone needs to find their way.",
    author: "Jennifer Dukes Lee"
  },
  {
    text: "Human kindness has never weakened the stamina of a free people. A nation does not have to be cruel to be tough.",
    author: "Franklin D. Roosevelt"
  },
  {
    text: "Be kind whenever possible. It is always possible.",
    author: "Dalai Lama"
  },
  {
    text: "A single act of kindness throws out roots in all directions, and the roots spring up and make new trees.",
    author: "Amelia Earhart"
  },
  {
    text: "The ideals which have lighted my way, and time after time have given me new courage to face life cheerfully, have been Kindness, Beauty, and Truth.",
    author: "Albert Einstein"
  },
  {
    text: "Constant kindness can accomplish much. As the sun makes ice melt, kindness causes misunderstanding, mistrust, and hostility to evaporate.",
    author: "Albert Schweitzer"
  },
  {
    text: "Practice random kindness and senseless acts of beauty.",
    author: "Anne Herbert"
  },
  {
    text: "No person was ever honored for what he received. Honor has been the reward for what he gave.",
    author: "Calvin Coolidge"
  },
  {
    text: "Success is not measured by what you accomplish, but by the opposition you have encountered, and the courage with which you have maintained the struggle against overwhelming odds.",
    author: "Orison Swett Marden"
  }
];

export function WeeklyInspiration() {
  const [currentQuote, setCurrentQuote] = useState<Quote>(inspirationalQuotes[0]);

  useEffect(() => {
    // Calculate which quote to show based on the current week
    const getWeeklyQuote = () => {
      const now = new Date();
      
      // Get the start of the current week (Sunday at 12:01 AM)
      const startOfWeek = new Date(now);
      startOfWeek.setDate(now.getDate() - now.getDay()); // Go to Sunday
      startOfWeek.setHours(0, 1, 0, 0); // Set to 12:01 AM
      
      // Calculate weeks since epoch (January 1, 1970)
      const epochStart = new Date(1970, 0, 1);
      const weeksSinceEpoch = Math.floor((startOfWeek.getTime() - epochStart.getTime()) / (7 * 24 * 60 * 60 * 1000));
      
      // Use modulo to cycle through quotes
      const quoteIndex = weeksSinceEpoch % inspirationalQuotes.length;
      
      return inspirationalQuotes[quoteIndex];
    };

    setCurrentQuote(getWeeklyQuote());
  }, []);

  return (
    <div className="w-full bg-gradient-to-r from-pink-50 to-rose-50 border border-pink-100 rounded-lg p-6 mb-6">
      <div className="flex items-start gap-4">
        {/* Heart Icon */}
        <div className="flex-shrink-0">
          <Heart className="h-8 w-8 text-red-500 stroke-2" />
        </div>
        
        {/* Content */}
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">
            Your weekly inspiration for helping others
          </h3>
          
          <blockquote className="text-gray-700 italic text-base leading-relaxed mb-2">
            "{currentQuote.text}"
          </blockquote>
          
          <cite className="text-sm font-medium text-gray-600">
            — {currentQuote.author}
          </cite>
        </div>
      </div>
    </div>
  );
}